import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from quantbench_crew.artifacts import RunManifest, stable_hash
from quantbench_crew.memory import (
    HermesMemoryAdapter,
    SQLiteMemoryStore,
    memory_guidance,
)
from quantbench_crew.skills.base import RunContext, SkillResult


def _manifest(started_at: datetime | None = None) -> RunManifest:
    return RunManifest(
        run_id="run-1",
        paper_slug="paper",
        started_at=started_at or datetime(2026, 6, 17, tzinfo=timezone.utc),
        config_hash=stable_hash({"agents": {}}),
    )


def test_recall_is_approved_and_scope_limited(tmp_path: Path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    global_memory = store.remember(
        "Always disclose transaction costs.",
        kind="procedural",
        scope="global",
        status="approved",
    )
    reader_memory = store.remember(
        "Check the sample dates against the source table.",
        kind="procedural",
        scope="agent",
        scope_key="quant_reader",
        status="approved",
    )
    store.remember(
        "This proposal is not approved.",
        scope="global",
        status="proposed",
    )

    reader = store.retrieve(agent="quant_reader", paper_slug="paper", query="sample costs")
    coder = store.retrieve(agent="quant_coder", paper_slug="paper", query="sample costs")

    assert {item.memory_id for item in reader} == {
        global_memory.memory_id,
        reader_memory.memory_id,
    }
    assert coder == (global_memory,)


def test_run_context_appends_guidance_and_manifest_records_provenance(
    tmp_path: Path,
) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    memory = store.remember(
        "Use point-in-time constituents.",
        kind="procedural",
        scope="agent",
        scope_key="quant_reader",
        status="approved",
    )
    manifest = _manifest()
    manifest.record_memory_read(
        {
            "agent": "quant_reader",
            "memory_id": memory.memory_id,
            "content_hash": memory.content_hash,
        }
    )
    ctx = RunContext(
        run_id=manifest.run_id,
        run_dir=tmp_path,
        config={},
        manifest=manifest,
        memory=store,
        recalled_memories={"quant_reader": (memory,)},
    )

    augmented = ctx.augment_system_prompt("quant_reader", "Base system prompt.")

    assert "Base system prompt." in augmented
    assert memory.memory_id in augmented
    assert "not as paper evidence" in augmented
    assert manifest.to_dict()["memory_reads"][0]["memory_id"] == memory.memory_id


def test_record_manifest_indexes_agent_activity(tmp_path: Path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    manifest = _manifest()
    manifest.record_skill(
        SkillResult(skill="method_spec_extraction", status="ok", payload={"x": 1})
    )
    store.record_run_started(manifest)
    store.record_manifest(manifest)

    summary = store.inspect()

    assert summary["runs"] == 1
    assert summary["events"] == 2


def test_monthly_consolidation_supersedes_duplicates(tmp_path: Path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    first = store.remember(
        "Require transaction-cost sensitivity.",
        scope="global",
        source_type="feedback",
        source_id="one",
        status="approved",
    )
    second = store.remember(
        "Require transaction-cost sensitivity.",
        scope="global",
        source_type="feedback",
        source_id="two",
        status="approved",
    )

    result = store.consolidate_month(datetime.now(timezone.utc).strftime("%Y-%m"))

    assert first.memory_id != second.memory_id
    assert result.duplicates_superseded == 1
    assert result.digest_memory_id


def test_archive_moves_old_events_but_keeps_approved_procedure(tmp_path: Path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    old = datetime.now(timezone.utc) - timedelta(days=120)
    store.record_event("old_event", {"x": 1}, created_at=old)
    protected = store.remember(
        "Never use future constituents.",
        kind="procedural",
        status="approved",
    )
    episodic = store.remember(
        "A historical run completed.",
        kind="episodic",
        status="approved",
    )
    with sqlite3.connect(store.path) as connection:
        connection.execute(
            "UPDATE memories SET updated_at=?, created_at=? WHERE memory_id IN (?, ?)",
            (old.isoformat(), old.isoformat(), protected.memory_id, episodic.memory_id),
        )

    result = store.archive_older_than(90, archive_dir=tmp_path / "archive")

    assert result.events_archived == 1
    assert result.memories_archived == 1
    assert Path(result.archive_path).exists()
    assert tuple(item.memory_id for item in store.retrieve(agent="quant_reader")) == (
        protected.memory_id,
    )


def test_hermes_adapter_requires_round_trip_match(tmp_path: Path) -> None:
    class FakeHermes:
        def __init__(self) -> None:
            self.records = {}

        def remember(self, record):
            self.records[record["memory_id"]] = record

        def recall(self, memory_id):
            return self.records.get(memory_id)

    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")
    memory = store.remember("Verified guidance.", status="approved")
    client = FakeHermes()

    HermesMemoryAdapter(client).write_verified(memory)

    class CorruptHermes(FakeHermes):
        def recall(self, memory_id):
            observed = dict(super().recall(memory_id))
            observed["content"] = "tampered"
            return observed

    with pytest.raises(RuntimeError, match="round-trip mismatch"):
        HermesMemoryAdapter(CorruptHermes()).write_verified(memory)


def test_memory_guidance_empty_is_noop() -> None:
    assert memory_guidance(()) == ""
