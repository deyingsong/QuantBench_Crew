import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from quantbench_crew.artifacts import RunManifest, stable_hash
from quantbench_crew.llm import (
    AnthropicClient,
    DEFAULT_MODEL,
    LLMResponse,
    ManifestLoggingClient,
    RecordedStubClient,
    RecordingClient,
    build_llm_client,
    estimate_cost_usd,
    request_fingerprint,
)


def _fixture_for(prompt: str, text: str, system: str = "") -> dict:
    fingerprint = request_fingerprint(DEFAULT_MODEL, prompt, system)
    return {
        fingerprint: {
            "text": text,
            "model": DEFAULT_MODEL,
            "input_tokens": 1000,
            "output_tokens": 500,
        }
    }


def _manifest() -> RunManifest:
    return RunManifest(
        run_id="run-1",
        paper_slug="slug",
        started_at=datetime(2026, 6, 10, tzinfo=timezone.utc),
        config_hash=stable_hash({}),
    )


def test_cost_estimation_uses_price_table() -> None:
    # claude-opus-4-8: $5 in / $25 out per MTok.
    assert estimate_cost_usd("claude-opus-4-8", 1000, 500) == pytest.approx(0.0175)
    assert estimate_cost_usd("unknown-model", 1000, 500) == 0.0


def test_recorded_stub_replays_fixture() -> None:
    client = RecordedStubClient(_fixture_for("What is momentum?", "A persistent anomaly."))

    response = client.complete("What is momentum?")

    assert response.text == "A persistent anomaly."
    assert response.model == DEFAULT_MODEL
    assert response.input_tokens == 1000
    assert response.cost_usd == pytest.approx(0.0175)
    assert response.fingerprint


def test_recorded_stub_raises_on_missing_fixture() -> None:
    client = RecordedStubClient({})

    with pytest.raises(LookupError, match="No recorded LLM fixture"):
        client.complete("never recorded")


def test_recorded_stub_distinguishes_system_prompts() -> None:
    client = RecordedStubClient(_fixture_for("q", "with system", system="be terse"))

    assert client.complete("q", system="be terse").text == "with system"
    with pytest.raises(LookupError):
        client.complete("q")


def test_recorded_stub_from_missing_path_is_empty(tmp_path: Path) -> None:
    client = RecordedStubClient.from_path(tmp_path / "absent.json")

    with pytest.raises(LookupError):
        client.complete("anything")


def test_manifest_logging_records_model_tokens_cost() -> None:
    manifest = _manifest()
    client = ManifestLoggingClient(
        RecordedStubClient(_fixture_for("q", "a")), manifest
    )

    response = client.complete("q")

    assert response.text == "a"
    assert len(manifest.llm_calls) == 1
    entry = manifest.llm_calls[0]
    assert entry["model"] == DEFAULT_MODEL
    assert entry["input_tokens"] == 1000
    assert entry["output_tokens"] == 500
    assert entry["cost_usd"] == pytest.approx(0.0175)
    assert entry["fingerprint"] == response.fingerprint
    # Raw prompt text stays out of the manifest; only sizes are recorded.
    assert "prompt" not in entry
    assert entry["prompt_chars"] == 1
    assert entry["status"] == "ok"


def test_manifest_logging_records_failed_completion() -> None:
    class FailingClient:
        name = "failing"
        _model = DEFAULT_MODEL

        def available(self) -> bool:
            return True

        def complete(self, prompt, *, system="", model=None, max_tokens=4096):
            raise OSError("rate limited")

    manifest = _manifest()
    client = ManifestLoggingClient(FailingClient(), manifest)

    with pytest.raises(OSError, match="rate limited"):
        client.complete("q", system="s")

    assert len(manifest.llm_calls) == 1
    entry = manifest.llm_calls[0]
    assert entry["client"] == "failing"
    assert entry["status"] == "failed"
    assert entry["error_type"] == "OSError"
    assert entry["error"] == "rate limited"
    assert entry["prompt_chars"] == 1
    assert entry["system_chars"] == 1
    assert "prompt" not in entry


class _FakeInnerClient:
    name = "fake"

    def available(self) -> bool:
        return True

    def complete(self, prompt, *, system="", model=None, max_tokens=4096):
        resolved = model or DEFAULT_MODEL
        return LLMResponse(
            text=f"echo:{prompt}",
            model=resolved,
            input_tokens=10,
            output_tokens=5,
            cost_usd=estimate_cost_usd(resolved, 10, 5),
            fingerprint=request_fingerprint(resolved, prompt, system),
        )


def test_recording_client_writes_replayable_fixtures(tmp_path: Path) -> None:
    fixture_path = tmp_path / "fixtures.json"
    recorder = RecordingClient(_FakeInnerClient(), fixture_path)

    recorded = recorder.complete("hello")

    saved = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert recorded.fingerprint in saved

    replayer = RecordedStubClient.from_path(fixture_path)
    replayed = replayer.complete("hello")
    assert replayed.text == "echo:hello"


def test_anthropic_client_unavailable_without_credentials(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    assert AnthropicClient().available() is False


def test_build_llm_client_provider_none_returns_none() -> None:
    assert build_llm_client({}) is None
    assert build_llm_client({"llm": {"provider": "none"}}) is None


def test_build_llm_client_stub_wrapped_with_manifest(tmp_path: Path) -> None:
    fixtures = tmp_path / "fixtures.json"
    fixtures.write_text(json.dumps(_fixture_for("q", "a")), encoding="utf-8")
    manifest = _manifest()

    client = build_llm_client(
        {"llm": {"provider": "stub", "fixtures": str(fixtures)}}, manifest
    )

    assert client is not None
    assert client.complete("q").text == "a"
    assert len(manifest.llm_calls) == 1


def test_build_llm_client_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Unknown llm provider"):
        build_llm_client({"llm": {"provider": "gpt-something"}})
