"""Provider-agnostic LLM client seam.

One ``complete()`` API with provider adapters and a recorded-stub mode that
replays fixtures in tests. Every call is logged to the run manifest with
model, token counts, and estimated cost — the manifest logs fingerprints and
sizes rather than raw prompt text, so manifests stay shareable and
deterministic while spend remains auditable per paper run.

Configured via the top-level ``llm:`` section of ``configs/agents.yaml``:

.. code-block:: yaml

    llm:
      provider: none        # none | stub | anthropic
      model: claude-opus-4-8
      max_tokens: 4096
      fixtures: tests/fixtures/llm_fixtures.json   # stub provider only

``provider: none`` keeps the dry workflow free of any LLM dependency.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Protocol, runtime_checkable

from quantbench_crew.artifacts import stable_hash

if TYPE_CHECKING:
    from quantbench_crew.artifacts import RunManifest

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 4096

# USD per million input/output tokens (cached from the Claude model catalog,
# 2026-05-26). Unknown models price at 0.0 so cost totals stay conservative
# lower bounds rather than guesses.
MODEL_PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-fable-5": (10.0, 50.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-opus-4-6": (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    input_price, output_price = MODEL_PRICES_PER_MTOK.get(model, (0.0, 0.0))
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


def request_fingerprint(model: str, prompt: str, system: str = "") -> str:
    """Deterministic identity of one completion request, used as fixture key."""

    return stable_hash({"model": model, "prompt": prompt, "system": system})


@dataclass(frozen=True)
class LLMResponse:
    """Result of one completion through the seam."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    fingerprint: str = ""


@runtime_checkable
class LLMClient(Protocol):
    """The single seam every LLM call in the pipeline routes through."""

    name: str

    def available(self) -> bool:
        ...

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        ...


class RecordedStubClient:
    """Replays recorded fixtures keyed by request fingerprint.

    The test-time backend: deterministic, offline, and loud when a fixture is
    missing so silent drift between prompts and recordings cannot happen.
    """

    name = "recorded-stub"

    def __init__(
        self,
        fixtures: Mapping[str, Mapping[str, Any]] | None = None,
        default_model: str = DEFAULT_MODEL,
    ) -> None:
        self._fixtures = {key: dict(value) for key, value in (fixtures or {}).items()}
        self._default_model = default_model

    @classmethod
    def from_path(cls, path: str | Path, default_model: str = DEFAULT_MODEL) -> "RecordedStubClient":
        fixture_path = Path(path)
        if not fixture_path.exists():
            return cls({}, default_model=default_model)
        return cls(
            json.loads(fixture_path.read_text(encoding="utf-8")),
            default_model=default_model,
        )

    def available(self) -> bool:
        return True

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        del max_tokens  # identity of a recorded completion ignores the cap
        resolved_model = model or self._default_model
        fingerprint = request_fingerprint(resolved_model, prompt, system)
        entry = self._fixtures.get(fingerprint)
        if entry is None:
            raise LookupError(
                "No recorded LLM fixture for this request "
                f"(model={resolved_model!r}, fingerprint={fingerprint[:16]}..., "
                f"prompt starts {prompt[:60]!r}). Record one with RecordingClient "
                "or add it to the fixtures file."
            )
        input_tokens = int(entry.get("input_tokens", 0))
        output_tokens = int(entry.get("output_tokens", 0))
        entry_model = str(entry.get("model", resolved_model))
        return LLMResponse(
            text=str(entry["text"]),
            model=entry_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=estimate_cost_usd(entry_model, input_tokens, output_tokens),
            fingerprint=fingerprint,
        )


class AnthropicClient:
    """Adapter over the official ``anthropic`` SDK (optional dependency).

    Sampling parameters are deliberately not exposed: current Opus-tier
    models reject temperature/top_p/top_k, and the pipeline's determinism
    story rests on recorded fixtures rather than sampling settings.
    """

    name = "anthropic"

    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None) -> None:
        self._model = model
        self._api_key = api_key

    def _credentials_present(self) -> bool:
        return bool(
            self._api_key
            or os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        )

    def available(self) -> bool:
        if not self._credentials_present():
            return False
        try:
            import anthropic  # noqa: F401
        except ImportError:
            return False
        return True

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        import anthropic

        client = (
            anthropic.Anthropic(api_key=self._api_key)
            if self._api_key
            else anthropic.Anthropic()
        )
        resolved_model = model or self._model
        request: dict[str, Any] = {
            "model": resolved_model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            request["system"] = system
        response = client.messages.create(**request)

        text = "".join(
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        )
        input_tokens = int(response.usage.input_tokens)
        output_tokens = int(response.usage.output_tokens)
        return LLMResponse(
            text=text,
            model=resolved_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=estimate_cost_usd(resolved_model, input_tokens, output_tokens),
            fingerprint=request_fingerprint(resolved_model, prompt, system),
        )


class RecordingClient:
    """Wraps a real client and persists each response as a replayable fixture."""

    name = "recording"

    def __init__(self, inner: LLMClient, path: str | Path) -> None:
        self._inner = inner
        self._path = Path(path)
        self._fixtures: dict[str, dict[str, Any]] = {}
        if self._path.exists():
            self._fixtures = json.loads(self._path.read_text(encoding="utf-8"))

    def available(self) -> bool:
        return self._inner.available()

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        response = self._inner.complete(
            prompt, system=system, model=model, max_tokens=max_tokens
        )
        fingerprint = response.fingerprint or request_fingerprint(
            response.model, prompt, system
        )
        self._fixtures[fingerprint] = {
            "text": response.text,
            "model": response.model,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._fixtures, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return response


class ManifestLoggingClient:
    """Decorator that records every completion in the run manifest."""

    def __init__(self, inner: LLMClient, manifest: "RunManifest") -> None:
        self._inner = inner
        self._manifest = manifest
        self.name = f"{inner.name}+manifest"

    def available(self) -> bool:
        return self._inner.available()

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        response = self._inner.complete(
            prompt, system=system, model=model, max_tokens=max_tokens
        )
        self._manifest.record_llm_call(
            {
                "client": self._inner.name,
                "model": response.model,
                "fingerprint": response.fingerprint,
                "prompt_chars": len(prompt),
                "system_chars": len(system),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
            }
        )
        return response


def build_llm_client(
    config: Mapping[str, Any], manifest: "RunManifest | None" = None
) -> LLMClient | None:
    """Construct the configured client; ``provider: none`` yields ``None``.

    When a manifest is supplied the client is wrapped so every call is
    logged — callers should always pass the run manifest so spend tracking
    cannot be bypassed.
    """

    llm_config = config.get("llm") or {}
    provider = str(llm_config.get("provider", "none")).lower()
    model = str(llm_config.get("model", DEFAULT_MODEL))

    client: LLMClient | None
    if provider in ("none", ""):
        client = None
    elif provider == "stub":
        fixtures = llm_config.get("fixtures", "tests/fixtures/llm_fixtures.json")
        client = RecordedStubClient.from_path(fixtures, default_model=model)
    elif provider == "anthropic":
        client = AnthropicClient(model=model)
    else:
        raise ValueError(f"Unknown llm provider: {provider!r}")

    if client is not None and manifest is not None:
        client = ManifestLoggingClient(client, manifest)
    return client
