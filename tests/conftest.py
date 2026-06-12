from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pytest

from quantbench_crew.artifacts import RunManifest, stable_hash
from quantbench_crew.skills.base import RunContext

_LLM_KEY_ENVS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "XAI_API_KEY",
    "GROK_API_KEY",
    "DEEPSEEK_API_KEY",
)


@pytest.fixture(autouse=True)
def _no_live_llm_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip provider keys so no test ever places a live LLM call.

    The shipped config defaults to per-agent live backbones (and the coder's
    code_generation skill is on by default), so tests that exercise default
    configs would otherwise go live on any developer machine with keys
    exported. Tests that need a key set one explicitly via monkeypatch.
    """

    for var in _LLM_KEY_ENVS:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def make_ctx(tmp_path: Path) -> Callable[..., RunContext]:
    """Build a RunContext backed by a temp run dir for skill tests."""

    def factory(config: dict[str, Any] | None = None, llm: Any = None) -> RunContext:
        manifest = RunManifest(
            run_id="test-run",
            paper_slug="test-slug",
            started_at=datetime(2026, 6, 10, tzinfo=timezone.utc),
            config_hash=stable_hash(config or {}),
        )
        run_dir = tmp_path / "test-run"
        run_dir.mkdir(parents=True, exist_ok=True)
        return RunContext(
            run_id="test-run",
            run_dir=run_dir,
            config=config or {},
            manifest=manifest,
            llm=llm,
        )

    return factory
