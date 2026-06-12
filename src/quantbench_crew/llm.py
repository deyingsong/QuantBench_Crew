"""Provider-agnostic LLM client seam.

One ``complete()`` API with provider adapters and a recorded-stub mode that
replays fixtures in tests. Every call is logged to the run manifest with
model, token counts, and estimated cost — the manifest logs fingerprints and
sizes rather than raw prompt text, so manifests stay shareable and
deterministic while spend remains auditable per paper run.

Five providers are supported: ``anthropic`` (Claude, via the official SDK),
and ``openai`` (GPT), ``gemini``, ``grok`` (xAI), ``deepseek`` — the latter
four through one stdlib HTTP adapter for the OpenAI-compatible chat API each
of them serves, so no extra packages are required. Each provider's "port" is
an API-key environment variable (overridable per agent via ``api_key_env``)
plus an overridable ``base_url``.

Configured via the top-level ``llm:`` section of ``configs/agents.yaml``:

.. code-block:: yaml

    llm:
      provider: per-agent   # none | stub | per-agent | <single provider>
      model: claude-opus-4-8                       # single-provider default
      fixtures: tests/fixtures/llm_fixtures.json   # stub provider only
      cost_cap_usd: 2.0
      agents:                                      # provider: per-agent
        quant_scout:    {provider: grok,      model: grok-4}
        quant_reader:   {provider: gemini,    model: gemini-2.5-pro}
        quant_coder:    {provider: anthropic, model: claude-opus-4-8}
        quant_bench:    {provider: deepseek,  model: deepseek-chat}
        quant_reviewer: {provider: openai,    model: gpt-5}

Fallback contract: backbones are checked at build time (key present, SDK
importable) and every live call is wrapped in skill-level try/except — when an
agent's backbone is missing or errors, *that agent alone* downgrades to its
deterministic offline fallback and the reason lands in the manifest.
``provider: none`` keeps the dry workflow free of any LLM dependency.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Mapping, Protocol, runtime_checkable

from quantbench_crew.agent_skills import compose_system, load_agent_skill
from quantbench_crew.artifacts import stable_hash

if TYPE_CHECKING:
    from quantbench_crew.artifacts import RunManifest

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_HTTP_TIMEOUT = 120.0

AGENT_NAMES = (
    "quant_scout",
    "quant_reader",
    "quant_coder",
    "quant_bench",
    "quant_reviewer",
)

# Per-provider ports: where requests go and which env var supplies the key.
# ``model`` is only the default; configs override per agent. The four
# OpenAI-compatible providers share one adapter; anthropic uses its SDK.
PROVIDER_DEFAULTS: dict[str, dict[str, Any]] = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "model": "gpt-5",
    },
    "gemini": {
        # Google's OpenAI-compatible endpoint for the Gemini API.
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "api_key_env": "GEMINI_API_KEY",
        "extra_key_envs": ("GOOGLE_API_KEY",),
        "model": "gemini-2.5-pro",
    },
    "grok": {
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
        "extra_key_envs": ("GROK_API_KEY",),
        "model": "grok-4",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
    },
    "anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "model": DEFAULT_MODEL,
    },
}

# Friendly names accepted in configs.
PROVIDER_ALIASES = {"gpt": "openai", "claude": "anthropic", "xai": "grok", "google": "gemini"}

# Route 1 default: drive headless Claude Code. Operators point this at any
# skill-supporting agent host (Codex CLI, Gemini CLI, ...) via per-agent
# ``harness_command``; {prompt}, {system}, {model} are substituted.
DEFAULT_HARNESS_COMMAND = ("claude", "-p", "{prompt}", "--model", "{model}")
DEFAULT_HARNESS_TIMEOUT = 300.0

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


Transport = Callable[[str, dict[str, str], dict[str, Any]], dict[str, Any]]


def _http_post_json(
    url: str, headers: dict[str, str], payload: dict[str, Any],
    timeout: float = DEFAULT_HTTP_TIMEOUT,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class OpenAICompatibleClient:
    """One stdlib adapter for every provider serving the OpenAI chat API.

    Covers GPT (api.openai.com), Gemini (Google's OpenAI-compatibility
    endpoint), Grok (api.x.ai), and DeepSeek — same request/response shape,
    different base URL and key. ``transport`` is injectable so tests exercise
    the adapter offline; network errors surface as ``OSError`` and are caught
    at the skill boundary, which is what triggers the per-agent offline
    fallback.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        api_key_env: str | None = None,
        price_per_mtok: tuple[float, float] | None = None,
        timeout: float = DEFAULT_HTTP_TIMEOUT,
        transport: Transport | None = None,
    ) -> None:
        defaults = PROVIDER_DEFAULTS.get(provider, {})
        self.name = provider
        self._model = model
        self._base_url = (base_url or defaults.get("base_url", "")).rstrip("/")
        self._api_key = api_key
        self._key_envs = tuple(
            env
            for env in (api_key_env or defaults.get("api_key_env"), *defaults.get("extra_key_envs", ()))
            if env
        )
        self._price = price_per_mtok
        self._timeout = timeout
        self._transport = transport or (
            lambda url, headers, payload: _http_post_json(url, headers, payload, self._timeout)
        )

    def _resolve_key(self) -> str | None:
        if self._api_key:
            return self._api_key
        for env in self._key_envs:
            value = os.environ.get(env)
            if value:
                return value
        return None

    def available(self) -> bool:
        return bool(self._base_url) and self._resolve_key() is not None

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        key = self._resolve_key()
        if key is None:
            raise OSError(
                f"no API key for provider {self.name!r} "
                f"(set one of: {', '.join(self._key_envs) or 'api_key'})"
            )
        resolved_model = model or self._model
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = self._transport(
            f"{self._base_url}/chat/completions",
            {"Authorization": f"Bearer {key}"},
            {"model": resolved_model, "messages": messages, "max_tokens": max_tokens},
        )
        try:
            text = str(data["choices"][0]["message"]["content"] or "")
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"malformed {self.name} response: {exc!r}") from exc
        usage = data.get("usage") or {}
        input_tokens = int(usage.get("prompt_tokens", 0))
        output_tokens = int(usage.get("completion_tokens", 0))
        if self._price is not None:
            cost = (input_tokens * self._price[0] + output_tokens * self._price[1]) / 1_000_000
        else:
            cost = estimate_cost_usd(resolved_model, input_tokens, output_tokens)
        return LLMResponse(
            text=text,
            model=resolved_model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
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

    def __init__(
        self,
        inner: LLMClient,
        manifest: "RunManifest",
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        self._inner = inner
        self._manifest = manifest
        self._extra = dict(extra or {})
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
                **self._extra,
            }
        )
        return response


class SkillAugmentedClient:
    """Prepends an agent's SKILL.md body to every system prompt (route 2).

    Transparent otherwise: the inner client's name is preserved so manifest
    entries and assignments still show the real backbone. Because the skill
    body becomes part of the system prompt, it participates in request
    fingerprints — editing a skill invalidates recorded fixtures for that
    agent, by design.
    """

    def __init__(self, inner: LLMClient, skill_body_composer: Callable[[str], str]) -> None:
        self._inner = inner
        self._compose = skill_body_composer
        self.name = inner.name

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
        return self._inner.complete(
            prompt, system=self._compose(system), model=model, max_tokens=max_tokens
        )


class HarnessClient:
    """Drive an agent-host CLI as an LLM backbone (route 1, the harness port).

    The host (headless Claude Code by default; any Agent-Skills-supporting
    CLI via ``harness_command``) is invoked per completion with {prompt},
    {system}, {model} substituted into the command template. When the
    template has no {system} slot the system prompt is prepended to the
    prompt text, so skill injection works for every host. Failures —
    executable missing, non-zero exit, timeout, empty output — raise
    ``OSError``, which the skill boundary converts into that agent's
    deterministic offline fallback.

    Token counts and cost are unknown for CLI hosts and recorded as zero;
    bound harness spend with iteration budgets (cost capture is a follow-up).
    """

    def __init__(
        self,
        provider: str,
        model: str,
        command: tuple[str, ...] | list[str] = DEFAULT_HARNESS_COMMAND,
        timeout: float = DEFAULT_HARNESS_TIMEOUT,
        runner: Callable[..., subprocess.CompletedProcess] | None = None,
    ) -> None:
        self.name = f"harness:{provider}"
        self._model = model
        self._command = list(command)
        self._timeout = timeout
        self._runner = runner or subprocess.run

    def available(self) -> bool:
        return bool(self._command) and shutil.which(self._command[0]) is not None

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        del max_tokens  # per-response caps are the host's concern
        resolved_model = model or self._model
        has_system_slot = any("{system}" in part for part in self._command)
        prompt_text = prompt if (has_system_slot or not system) else f"{system}\n\n{prompt}"
        argv = [
            part.replace("{prompt}", prompt_text)
            .replace("{system}", system)
            .replace("{model}", resolved_model)
            for part in self._command
        ]
        try:
            completed = self._runner(
                argv, capture_output=True, text=True, timeout=self._timeout
            )
        except subprocess.TimeoutExpired as exc:
            raise OSError(f"harness {argv[0]!r} timed out after {self._timeout}s") from exc
        if completed.returncode != 0:
            tail = (completed.stderr or "").strip().splitlines()[-1:] or ["no stderr"]
            raise OSError(f"harness {argv[0]!r} exited {completed.returncode}: {tail[0]}")
        text = (completed.stdout or "").strip()
        if not text:
            raise OSError(f"harness {argv[0]!r} produced no output")
        return LLMResponse(
            text=text,
            model=resolved_model,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            fingerprint=request_fingerprint(resolved_model, prompt, system),
        )


class PerAgentLLMRouter:
    """Routes each agent to its own backbone, with per-agent offline fallback.

    ``for_agent`` returns the agent's (manifest-logged) client, or ``None``
    when that backbone is not configured or failed its build-time
    availability check — the skill then takes its deterministic offline path
    for that agent alone. ``reasons`` records why a backbone is offline so
    the degradation is auditable rather than silent.
    """

    name = "per-agent"

    def __init__(
        self,
        clients: Mapping[str, LLMClient | None],
        reasons: Mapping[str, str] | None = None,
    ) -> None:
        self._clients = dict(clients)
        self.reasons = dict(reasons or {})

    def for_agent(self, agent: str) -> LLMClient | None:
        return self._clients.get(agent)

    def assignments(self) -> dict[str, str | None]:
        """agent -> backbone client name (None when offline)."""

        return {
            agent: (client.name if client is not None else None)
            for agent, client in self._clients.items()
        }

    def available(self) -> bool:
        return any(client is not None for client in self._clients.values())

    def complete(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> LLMResponse:
        raise RuntimeError(
            "PerAgentLLMRouter has no default backbone; resolve a client with "
            "llm_for_agent(ctx.llm, '<agent_name>') before calling complete()."
        )


def llm_for_agent(llm: Any, agent: str) -> LLMClient | None:
    """Resolve the client one agent should use from ``RunContext.llm``.

    Handles all three shapes: None (no LLM), a single shared client
    (none/stub/single-provider modes), or a PerAgentLLMRouter.
    """

    if llm is None:
        return None
    if isinstance(llm, PerAgentLLMRouter):
        return llm.for_agent(agent)
    return llm


def _normalize_provider(provider: str) -> str:
    provider = provider.lower().strip()
    return PROVIDER_ALIASES.get(provider, provider)


def _single_client(
    provider: str, model: str, settings: Mapping[str, Any]
) -> LLMClient:
    """Construct one un-wrapped provider client (no manifest logging)."""

    provider = _normalize_provider(provider)
    if provider == "stub":
        fixtures = settings.get("fixtures", "tests/fixtures/llm_fixtures.json")
        return RecordedStubClient.from_path(fixtures, default_model=model)
    if provider == "anthropic":
        return AnthropicClient(model=model, api_key=settings.get("api_key"))
    if provider in PROVIDER_DEFAULTS:
        price = settings.get("price_per_mtok")
        return OpenAICompatibleClient(
            provider,
            model,
            base_url=settings.get("base_url"),
            api_key=settings.get("api_key"),
            api_key_env=settings.get("api_key_env"),
            price_per_mtok=tuple(price) if price else None,
            timeout=float(settings.get("timeout", DEFAULT_HTTP_TIMEOUT)),
        )
    raise ValueError(
        f"Unknown llm provider: {provider!r}; expected one of "
        f"{sorted((*PROVIDER_DEFAULTS, 'stub', 'none', 'per-agent'))}"
    )


def build_llm_client(
    config: Mapping[str, Any], manifest: "RunManifest | None" = None
) -> LLMClient | PerAgentLLMRouter | None:
    """Construct the configured client; ``provider: none`` yields ``None``.

    ``provider: per-agent`` builds a router with one backbone per agent from
    ``llm.agents``; each backbone is availability-checked at build time and
    routes to ``None`` (offline fallback) when its key or SDK is missing.
    When a manifest is supplied every live client is wrapped so each call is
    logged with its agent and provider — callers should always pass the run
    manifest so spend tracking cannot be bypassed.
    """

    llm_config = config.get("llm") or {}
    provider = str(llm_config.get("provider", "none")).lower()
    model = str(llm_config.get("model", DEFAULT_MODEL))

    if provider in ("none", ""):
        return None

    if provider == "per-agent":
        agent_entries = llm_config.get("agents") or {}
        skills_dir = llm_config.get("skills_dir", "skills")
        clients: dict[str, LLMClient | None] = {}
        reasons: dict[str, str] = {}
        for agent in AGENT_NAMES:
            entry = agent_entries.get(agent) or {}
            agent_provider = str(entry.get("provider", "")).strip()
            if not agent_provider:
                clients[agent] = None
                reasons[agent] = "no backbone configured"
                continue
            agent_model = str(
                entry.get("model")
                or PROVIDER_DEFAULTS.get(_normalize_provider(agent_provider), {}).get(
                    "model", model
                )
            )

            mode = str(entry.get("mode", "api")).lower()
            if mode == "harness":
                # Route 1: drive an agent-host CLI instead of the bare API.
                client: LLMClient = HarnessClient(
                    _normalize_provider(agent_provider),
                    agent_model,
                    command=entry.get("harness_command", DEFAULT_HARNESS_COMMAND),
                    timeout=float(entry.get("harness_timeout", DEFAULT_HARNESS_TIMEOUT)),
                )
            elif mode == "api":
                client = _single_client(agent_provider, agent_model, {**llm_config, **entry})
            else:
                raise ValueError(
                    f"unknown llm mode {mode!r} for {agent}; expected 'api' or 'harness'"
                )

            if not client.available():
                clients[agent] = None
                reasons[agent] = (
                    f"backbone {client.name!r} unavailable "
                    f"({'host CLI not on PATH' if mode == 'harness' else 'missing API key or SDK'}); "
                    "deterministic offline fallback in effect"
                )
                continue
            if manifest is not None:
                client = ManifestLoggingClient(
                    client, manifest, extra={"agent": agent, "provider": client.name}
                )
            # Route 2 (default): inject the agent's SKILL.md into every system
            # prompt. Outermost wrapper, so logged sizes and fingerprints see
            # the augmented system. Disabled by skills_dir: "" / false.
            if skills_dir:
                skill = load_agent_skill(agent, skills_dir)
                if skill is not None:
                    client = SkillAugmentedClient(
                        client, lambda system, _s=skill: compose_system(_s, system)
                    )
            clients[agent] = client
        return PerAgentLLMRouter(clients, reasons)

    client = _single_client(provider, model, llm_config)
    if manifest is not None:
        client = ManifestLoggingClient(client, manifest)
    return client
