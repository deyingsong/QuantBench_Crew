"""Per-agent LLM backbones: provider ports, routing, and offline fallback."""

import json

import pytest

from quantbench_crew.artifacts import RunManifest, stable_hash
from quantbench_crew.llm import (
    AGENT_NAMES,
    AnthropicClient,
    DEFAULT_MODEL,
    ManifestLoggingClient,
    OpenAICompatibleClient,
    PROVIDER_DEFAULTS,
    PerAgentLLMRouter,
    RecordedStubClient,
    build_llm_client,
    llm_for_agent,
    request_fingerprint,
)
from quantbench_crew.models import Paper, PaperAnalysis
from quantbench_crew.skills.reader.method_spec import (
    MethodSpecExtractionSkill,
    SYSTEM_PROMPT as READER_SYSTEM,
    build_method_spec_prompt,
)

ALL_KEY_ENVS = (
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "XAI_API_KEY",
    "GROK_API_KEY",
    "DEEPSEEK_API_KEY",
)

PER_AGENT_CONFIG = {
    "llm": {
        "provider": "per-agent",
        "cost_cap_usd": 2.0,
        "agents": {
            "quant_scout": {"provider": "grok", "model": "grok-4"},
            "quant_reader": {"provider": "gemini", "model": "gemini-2.5-pro"},
            "quant_coder": {"provider": "anthropic", "model": "claude-opus-4-8"},
            "quant_bench": {"provider": "deepseek", "model": "deepseek-chat"},
            "quant_reviewer": {"provider": "openai", "model": "gpt-5"},
        },
    }
}


def _clear_keys(monkeypatch) -> None:
    for env in ALL_KEY_ENVS:
        monkeypatch.delenv(env, raising=False)


def _manifest() -> RunManifest:
    from datetime import datetime, timezone

    return RunManifest(
        run_id="r",
        paper_slug="s",
        started_at=datetime(2026, 6, 11, tzinfo=timezone.utc),
        config_hash=stable_hash({}),
    )


def test_provider_defaults_cover_all_five_backbones() -> None:
    assert set(PROVIDER_DEFAULTS) == {"openai", "gemini", "grok", "deepseek", "anthropic"}
    for name, defaults in PROVIDER_DEFAULTS.items():
        assert defaults.get("api_key_env"), name
        assert defaults.get("model"), name
        if name != "anthropic":  # anthropic goes through its SDK, not HTTP
            assert defaults.get("base_url"), name


def test_openai_compatible_request_response_and_cost() -> None:
    captured = {}

    def transport(url, headers, payload):
        captured.update(url=url, headers=headers, payload=payload)
        return {
            "choices": [{"message": {"content": "forty-two"}}],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 500},
        }

    client = OpenAICompatibleClient(
        "deepseek",
        "deepseek-chat",
        api_key="sk-test",
        price_per_mtok=(1.0, 2.0),
        transport=transport,
    )
    response = client.complete("meaning of life?", system="be brief")

    assert captured["url"] == "https://api.deepseek.com/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer sk-test"
    assert captured["payload"]["model"] == "deepseek-chat"
    assert captured["payload"]["messages"][0] == {"role": "system", "content": "be brief"}
    assert captured["payload"]["messages"][1]["role"] == "user"
    assert response.text == "forty-two"
    assert response.input_tokens == 1000 and response.output_tokens == 500
    assert response.cost_usd == pytest.approx((1000 * 1.0 + 500 * 2.0) / 1_000_000)
    assert response.fingerprint


def test_openai_compatible_unavailable_without_key(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    client = OpenAICompatibleClient("grok", "grok-4")

    assert client.available() is False
    with pytest.raises(OSError, match="XAI_API_KEY"):
        client.complete("hello")


def test_openai_compatible_reads_key_from_port_env(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-port")

    assert OpenAICompatibleClient("deepseek", "deepseek-chat").available() is True
    # Alternate accepted env for gemini.
    monkeypatch.setenv("GOOGLE_API_KEY", "g-key")
    assert OpenAICompatibleClient("gemini", "gemini-2.5-pro").available() is True


def test_anthropic_client_supports_custom_key_env(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    monkeypatch.setenv("CLAUDE_API_KEY", "claude-port")

    client = AnthropicClient("claude-opus-4-8", api_key_env="CLAUDE_API_KEY")

    assert client._resolve_key() == "claude-port"


def test_malformed_response_raises_value_error() -> None:
    client = OpenAICompatibleClient(
        "openai", "gpt-5", api_key="k", transport=lambda *a: {"unexpected": True}
    )
    with pytest.raises(ValueError, match="malformed openai response"):
        client.complete("q")


def test_router_all_backbones_offline_without_keys(monkeypatch) -> None:
    _clear_keys(monkeypatch)

    router = build_llm_client(PER_AGENT_CONFIG, _manifest())

    assert isinstance(router, PerAgentLLMRouter)
    assert router.available() is False
    for agent in AGENT_NAMES:
        assert router.for_agent(agent) is None
        assert llm_for_agent(router, agent) is None
        assert "unavailable" in router.reasons[agent]
    assert set(router.assignments().values()) == {None}


def test_router_brings_up_only_keyed_backbones(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    monkeypatch.setenv("XAI_API_KEY", "x-key")

    router = build_llm_client(PER_AGENT_CONFIG, _manifest())

    scout = router.for_agent("quant_scout")
    assert scout is not None and scout.name == "grok+manifest"
    assert router.assignments()["quant_scout"] == "grok+manifest"
    # Every other agent stays offline, independently.
    for agent in set(AGENT_NAMES) - {"quant_scout"}:
        assert router.for_agent(agent) is None


def test_router_refuses_default_complete() -> None:
    router = PerAgentLLMRouter({agent: None for agent in AGENT_NAMES})
    with pytest.raises(RuntimeError, match="llm_for_agent"):
        router.complete("q")


def test_llm_for_agent_passthrough_for_shared_clients() -> None:
    stub = RecordedStubClient({})

    assert llm_for_agent(None, "quant_reader") is None
    assert llm_for_agent(stub, "quant_reader") is stub


def test_manifest_logging_records_agent_and_provider() -> None:
    prompt = "q"
    fixtures = {
        request_fingerprint(DEFAULT_MODEL, prompt, ""): {
            "text": "a",
            "model": DEFAULT_MODEL,
            "input_tokens": 10,
            "output_tokens": 5,
        }
    }
    manifest = _manifest()
    client = ManifestLoggingClient(
        RecordedStubClient(fixtures), manifest,
        extra={"agent": "quant_reader", "provider": "gemini"},
    )

    client.complete(prompt)

    entry = manifest.llm_calls[0]
    assert entry["agent"] == "quant_reader"
    assert entry["provider"] == "gemini"
    assert entry["cost_usd"] >= 0.0


def _golden_analysis() -> PaperAnalysis:
    paper = Paper(title="Momentum Everywhere", abstract="Past 6-month returns.")
    return PaperAnalysis(
        paper=paper,
        research_question="q",
        proposed_method="momentum",
        assumptions=(),
        datasets=("returns",),
        metrics=("sharpe",),
        limitations=(),
    )


def test_reader_skill_falls_back_when_its_backbone_is_offline(make_ctx) -> None:
    ctx = make_ctx()
    ctx.llm = PerAgentLLMRouter({agent: None for agent in AGENT_NAMES})

    result = MethodSpecExtractionSkill().run(ctx, analysis=_golden_analysis())

    assert result.status == "ok"
    assert result.payload["source"] == "metadata_fallback"
    assert any("no LLM configured for quant_reader" in note for note in result.notes)


def test_reader_skill_uses_its_routed_backbone(make_ctx) -> None:
    analysis = _golden_analysis()
    prompt = build_method_spec_prompt(analysis)
    spec_json = json.dumps(
        {
            "universe": "US common stocks",
            "frequency": "monthly",
            "signal_definition": "past 6-month return",
            "portfolio_construction": "decile long-short",
            "rebalance_frequency": "monthly",
            "holding_period": "6 months",
            "confidence": 0.9,
        }
    )
    fixtures = {
        request_fingerprint(DEFAULT_MODEL, prompt, READER_SYSTEM): {
            "text": spec_json,
            "model": DEFAULT_MODEL,
            "input_tokens": 100,
            "output_tokens": 50,
        }
    }
    ctx = make_ctx()
    ctx.llm = PerAgentLLMRouter(
        {**{agent: None for agent in AGENT_NAMES}, "quant_reader": RecordedStubClient(fixtures)}
    )

    result = MethodSpecExtractionSkill().run(ctx, analysis=analysis)

    assert result.payload["source"] == "llm"
    assert result.payload["method_spec"]["frequency"] == "monthly"


def test_single_provider_aliases_and_unknown(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    client = build_llm_client({"llm": {"provider": "gpt", "model": "gpt-5"}})
    assert client is not None and client.name == "openai"

    with pytest.raises(ValueError, match="Unknown llm provider"):
        build_llm_client({"llm": {"provider": "watson"}})
