import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from quantbench_crew.artifacts import (
    ArtifactStore,
    MANIFEST_FILENAME,
    RunManifest,
    new_run_id,
    sha256_text,
    stable_hash,
    start_run,
)
from quantbench_crew.skills.base import SkillResult


def _manifest(run_id: str, started_at: datetime) -> RunManifest:
    return RunManifest(
        run_id=run_id,
        paper_slug="momentum-everywhere",
        started_at=started_at,
        config_hash=stable_hash({"agents": {}}),
    )


def test_stable_hash_is_order_invariant() -> None:
    assert stable_hash({"b": 1, "a": [1, 2]}) == stable_hash({"a": [1, 2], "b": 1})
    assert stable_hash({"a": 1}) != stable_hash({"a": 2})


def test_content_hash_excludes_volatile_fields() -> None:
    first = _manifest("run-1", datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc))
    second = _manifest("run-2", datetime(2026, 6, 11, 9, 30, tzinfo=timezone.utc))
    for manifest in (first, second):
        manifest.record_seed("global", 0)
        manifest.record_artifact("report.md", sha256_text("same content"))
        manifest.record_skill(SkillResult(skill="demo", status="ok"))

    assert first.content_hash() == second.content_hash()


def test_content_hash_changes_with_content() -> None:
    base = _manifest("run-1", datetime(2026, 6, 10, tzinfo=timezone.utc))
    changed = _manifest("run-1", datetime(2026, 6, 10, tzinfo=timezone.utc))
    base.record_artifact("report.md", sha256_text("one"))
    changed.record_artifact("report.md", sha256_text("two"))

    assert base.content_hash() != changed.content_hash()


def test_save_writes_manifest_json_with_content_hash(tmp_path: Path) -> None:
    manifest = _manifest("run-1", datetime(2026, 6, 10, tzinfo=timezone.utc))
    manifest.record_llm_call({"model": "claude-opus-4-8", "cost_usd": 0.01})

    path = manifest.save(tmp_path / "run-1")

    assert path.name == MANIFEST_FILENAME
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["content_hash"] == manifest.content_hash()
    assert payload["paper_slug"] == "momentum-everywhere"
    assert payload["llm_calls"][0]["model"] == "claude-opus-4-8"


def test_artifact_store_writes_and_hashes(tmp_path: Path) -> None:
    manifest = _manifest("run-1", datetime(2026, 6, 10, tzinfo=timezone.utc))
    store = ArtifactStore(tmp_path / "run-1", manifest)

    target = store.write_text("report.md", "# Report")
    store.write_json("nested/data.json", {"b": 2, "a": 1})

    assert target.read_text(encoding="utf-8") == "# Report"
    assert manifest.artifacts["report.md"] == sha256_text("# Report")
    assert "nested/data.json" in manifest.artifacts
    assert (tmp_path / "run-1" / "nested" / "data.json").exists()


def test_artifact_store_rejects_escaping_paths(tmp_path: Path) -> None:
    manifest = _manifest("run-1", datetime(2026, 6, 10, tzinfo=timezone.utc))
    store = ArtifactStore(tmp_path / "run-1", manifest)

    with pytest.raises(ValueError, match="inside the run directory"):
        store.write_text("../evil.md", "nope")
    with pytest.raises(ValueError, match="inside the run directory"):
        store.write_text("/abs/evil.md", "nope")


def test_start_run_reruns_produce_identical_content_hash(tmp_path: Path) -> None:
    config = {"agents": {"quant_scout": {"role": "scout"}}}

    first_manifest, first_store = start_run(tmp_path, "paper-slug", config)
    first_store.write_text("report.md", "identical body")
    first_manifest.save(first_store.run_dir)

    second_manifest, second_store = start_run(tmp_path, "paper-slug", config)
    second_store.write_text("report.md", "identical body")
    second_manifest.save(second_store.run_dir)

    assert first_manifest.run_id != second_manifest.run_id
    assert first_manifest.content_hash() == second_manifest.content_hash()


def test_new_run_id_contains_slug_and_sorts_by_time() -> None:
    early = new_run_id("slug", datetime(2026, 1, 1, tzinfo=timezone.utc))
    late = new_run_id("slug", datetime(2026, 1, 2, tzinfo=timezone.utc))

    assert "slug" in early
    assert early < late
