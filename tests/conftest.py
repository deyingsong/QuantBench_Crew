from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pytest

from quantbench_crew.artifacts import RunManifest, stable_hash
from quantbench_crew.skills.base import RunContext


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
