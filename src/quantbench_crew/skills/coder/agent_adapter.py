"""Agentic codegen backend: the reserved ``agent`` adapter (QB-31).

The QB-11 seam has two generation adapters: ``complete`` (single-shot through
the LLM seam) and ``agent`` (this one). The agent adapter swaps the *source
generator* for a headless Claude Code / Agent SDK call while the surrounding
ERA search and the sandbox test-oracle stay exactly as in ``complete`` mode —
so failures still feed back, the per-paper cost cap still bounds the loop, and
every candidate still runs through the deterministic templates before it
counts. Keeping the sandbox as the oracle (rather than trusting the agent's
own test run) preserves the security and anti-Goodhart properties.

The real backend shells out to the ``claude`` CLI and is gated by
``available()`` (CLI present + credentials). In tests and CI it is absent, so
the adapter falls back to ``complete`` (or the deterministic reference) and
records why. Tests inject a stub backend.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any, Mapping, Protocol, runtime_checkable


@runtime_checkable
class AgentBackend(Protocol):
    """A source generator for the agent adapter."""

    name: str

    def available(self) -> bool:
        ...

    def generate(self, prompt: str, system: str, feedback: str = "") -> str:
        """Return candidate module text (may be fenced) for a prompt."""
        ...


class HeadlessClaudeBackend:
    """Headless Claude Code (`claude -p`) as the codegen agent.

    Availability requires the ``claude`` CLI on PATH and Anthropic credentials
    in the environment. The exact invocation may need tuning per CLI version;
    it is intentionally simple and never runs in CI (gated off by
    ``available()``).
    """

    name = "headless-claude"

    def __init__(self, model: str = "claude-opus-4-8", timeout: float = 180.0) -> None:
        self._model = model
        self._timeout = timeout

    def available(self) -> bool:
        has_cli = shutil.which("claude") is not None
        has_creds = bool(
            os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        )
        return has_cli and has_creds

    def generate(self, prompt: str, system: str, feedback: str = "") -> str:
        combined = system + "\n\n" + prompt
        if feedback:
            combined += "\n\n" + feedback
        completed = subprocess.run(
            ["claude", "-p", combined, "--model", self._model],
            capture_output=True,
            text=True,
            timeout=self._timeout,
        )
        return completed.stdout


class StubAgentBackend:
    """Deterministic in-memory backend for tests: replays a fixed source."""

    name = "stub-agent"

    def __init__(self, source: str, available: bool = True) -> None:
        self._source = source
        self._available = available
        self.calls = 0

    def available(self) -> bool:
        return self._available

    def generate(self, prompt: str, system: str, feedback: str = "") -> str:
        self.calls += 1
        return self._source


def resolve_agent_backend(settings: Mapping[str, Any]) -> AgentBackend:
    """Construct the configured agent backend (default: headless Claude)."""

    model = str(settings.get("model", "claude-opus-4-8"))
    timeout = float(settings.get("agent_timeout", 180.0))
    return HeadlessClaudeBackend(model=model, timeout=timeout)
