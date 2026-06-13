import json
from datetime import date
from pathlib import Path

from quantbench_crew.models import Paper, RelevanceAssessment, ScoredPaper
from quantbench_crew.tools.paper_queue import (
    ResearchQueue,
    deduplicate_papers,
    filter_by_online_date,
    paper_online_date,
    parse_iso_date,
)


def test_strict_date_filter_requires_day_precision() -> None:
    inside = Paper(title="inside", abstract="", published=date(2026, 6, 1))
    outside = Paper(title="outside", abstract="", published=date(2026, 6, 11))
    year_only = Paper(
        title="year only",
        abstract="",
        published=date(2026, 1, 1),
        raw={"date_precision": "year"},
    )

    result = filter_by_online_date(
        [inside, outside, year_only], date(2026, 5, 31), date(2026, 6, 10)
    )

    assert result.in_window == (inside,)
    assert result.outside_window == (outside,)
    assert result.missing_exact_date == (year_only,)
    assert paper_online_date(year_only) is None


def test_parse_iso_date_rejects_ambiguous_input() -> None:
    assert parse_iso_date("2026-06-10") == date(2026, 6, 10)
    try:
        parse_iso_date("June 10")
    except ValueError as exc:
        assert "YYYY-MM-DD" in str(exc)
    else:
        raise AssertionError("ambiguous date should fail")


def test_deduplicate_prefers_richer_record() -> None:
    sparse = Paper(title="Same", abstract="", raw={"doi": "10/x"})
    rich = Paper(title="Different provider title", abstract="Detailed abstract", raw={"doi": "10/X"})

    assert deduplicate_papers([sparse, rich]) == [rich]


def test_queue_refresh_preserves_human_decisions(tmp_path: Path) -> None:
    path = tmp_path / "queue.json"
    paper = Paper(
        title="Paper",
        abstract="Detailed evidence.",
        published=date(2026, 6, 1),
        raw={"doi": "10/x"},
    )
    assessment = RelevanceAssessment(score=0.8, method="research_value_rubric")
    first = ScoredPaper(paper=paper, score=8.0, relevance=assessment)
    queue = ResearchQueue(path)
    queue.upsert([first], date(2026, 5, 31), date(2026, 6, 10), as_of=date(2026, 6, 10))
    queue.save()

    payload = json.loads(path.read_text())
    payload["entries"][0]["status"] = "promoted"
    payload["entries"][0]["notes"] = "Read methods next."
    path.write_text(json.dumps(payload))

    refreshed = ResearchQueue(path)
    second = ScoredPaper(paper=paper, score=9.0, relevance=assessment)
    update = refreshed.upsert(
        [second], date(2026, 5, 31), date(2026, 6, 10), as_of=date(2026, 6, 11)
    )
    refreshed.save()

    entry = json.loads(path.read_text())["entries"][0]
    assert update.added == 0 and update.updated == 1
    assert entry["status"] == "promoted"
    assert entry["notes"] == "Read methods next."
    assert entry["first_seen"] == "2026-06-10"
    assert entry["last_seen"] == "2026-06-11"
