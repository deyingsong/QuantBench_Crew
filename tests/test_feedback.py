import json
from pathlib import Path

from quantbench_crew.feedback import (
    FEEDBACK_END,
    FEEDBACK_START,
    ensure_feedback_section,
    extract_human_notes,
    ingest_report_feedback,
    merge_preserved_feedback,
    report_metadata,
)
from quantbench_crew.memory import SQLiteMemoryStore


def test_feedback_section_has_bounded_markers_and_metadata() -> None:
    report = ensure_feedback_section(
        "# Paper\n\nBody",
        run_id="run-1",
        paper_slug="paper",
    )

    assert FEEDBACK_START in report
    assert FEEDBACK_END in report
    assert extract_human_notes(report) == ""
    assert report_metadata(report) == {"run_id": "run-1", "paper_slug": "paper"}


def test_regeneration_preserves_existing_human_notes() -> None:
    existing = ensure_feedback_section(
        "# Old\n\nOld body", run_id="run-1", paper_slug="paper"
    ).replace(
        FEEDBACK_START + "\n",
        FEEDBACK_START + "\nThe benchmark should include delisting returns.\n",
    )

    merged = merge_preserved_feedback(
        "# New\n\nNew body",
        existing,
        run_id="run-2",
        paper_slug="paper",
    )

    assert "New body" in merged
    assert "Old body" not in merged
    assert extract_human_notes(merged) == (
        "The benchmark should include delisting returns."
    )
    assert report_metadata(merged)["run_id"] == "run-2"


def test_feedback_ingestion_is_idempotent_and_requires_approval(tmp_path: Path) -> None:
    report_path = tmp_path / "paper.md"
    report = ensure_feedback_section(
        "# Paper\n\nBody", run_id="run-1", paper_slug="paper"
    ).replace(
        FEEDBACK_START + "\n",
        FEEDBACK_START
        + "\nThe quant_bench method must include delisting returns in the dataset.\n",
    )
    report_path.write_text(report, encoding="utf-8")
    store = SQLiteMemoryStore(tmp_path / "memory.sqlite3")

    first, first_created = ingest_report_feedback(report_path, store)
    second, second_created = ingest_report_feedback(report_path, store)

    assert first_created is True
    assert second_created is False
    assert first.feedback_id == second.feedback_id
    assert first.status == "proposed"
    assert first.category == "method_gap"
    assert first.scope == "agent"
    assert first.scope_key == "quant_bench"
    assert store.retrieve(agent="quant_bench", paper_slug="paper") == ()

    memory = store.approve_feedback(first.feedback_id, reviewer="expert")

    recalled = store.retrieve(agent="quant_bench", paper_slug="paper")
    assert recalled == (memory,)
    assert recalled[0].kind == "prospective"


def test_feedback_cli_metadata_is_valid_json_shape(tmp_path: Path) -> None:
    report = ensure_feedback_section(
        "# Paper\n", run_id="run-json", paper_slug="paper-json"
    )
    metadata = report_metadata(report)

    assert json.loads(json.dumps(metadata))["run_id"] == "run-json"
