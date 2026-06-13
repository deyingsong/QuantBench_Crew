"""Date-window filtering, cross-source deduplication, and durable paper queues."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from quantbench_crew.models import Paper, ScoredPaper

DEFAULT_QUEUE_PATH = Path("data/processed/paper_queue.json")
QUEUE_STATUSES = ("queued", "promoted", "deferred", "rejected", "analyzed")


@dataclass(frozen=True)
class DateFilterResult:
    """Result of applying a strict inclusive online-date window."""

    in_window: tuple[Paper, ...]
    outside_window: tuple[Paper, ...]
    missing_exact_date: tuple[Paper, ...]


@dataclass(frozen=True)
class QueueUpdate:
    """Counts produced by one queue upsert."""

    added: int
    updated: int
    total: int


def parse_iso_date(value: str, label: str = "date") -> date:
    """Parse an explicit ISO date, rejecting ambiguous date expressions."""

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO date in YYYY-MM-DD form: {value!r}") from exc


def paper_online_date(paper: Paper) -> date | None:
    """Return a defensible day-level online date, or None when precision is weaker."""

    precision = str(paper.raw.get("date_precision") or "day").lower()
    if precision not in {"day", "date", "exact"}:
        return None
    if paper.published is not None:
        return paper.published
    for key in ("online_date", "publication_date", "published", "created"):
        parsed = _coerce_date(paper.raw.get(key))
        if parsed is not None:
            return parsed
    return None


def filter_by_online_date(
    papers: Iterable[Paper], start_date: date, end_date: date
) -> DateFilterResult:
    """Filter papers to an inclusive date window without guessing missing dates."""

    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")
    inside: list[Paper] = []
    outside: list[Paper] = []
    missing: list[Paper] = []
    for paper in papers:
        online = paper_online_date(paper)
        if online is None:
            missing.append(paper)
        elif start_date <= online <= end_date:
            inside.append(paper)
        else:
            outside.append(paper)
    return DateFilterResult(tuple(inside), tuple(outside), tuple(missing))


def paper_identity(paper: Paper) -> str:
    """Return a stable cross-source identity, preferring DOI and arXiv id."""

    doi = str(paper.raw.get("doi") or "").strip().lower()
    if doi:
        return f"doi:{doi}"
    arxiv_id = str(paper.raw.get("arxiv_id") or "").strip().lower()
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    if paper.url:
        normalized = paper.url.strip().lower().rstrip("/")
        if normalized:
            return f"url:{normalized}"
    title = " ".join(paper.title.lower().split())
    return f"title:{hashlib.sha256(title.encode('utf-8')).hexdigest()[:16]}"


def deduplicate_papers(papers: Iterable[Paper]) -> list[Paper]:
    """Deduplicate candidates while retaining the richest metadata record."""

    selected: dict[str, Paper] = {}
    order: list[str] = []
    for paper in papers:
        identity = paper_identity(paper)
        if identity not in selected:
            selected[identity] = paper
            order.append(identity)
        elif _metadata_richness(paper) > _metadata_richness(selected[identity]):
            selected[identity] = paper
    return [selected[identity] for identity in order]


class ResearchQueue:
    """Persistent ranked queue that preserves human status and notes on refresh."""

    def __init__(self, path: str | Path = DEFAULT_QUEUE_PATH) -> None:
        self.path = Path(path)
        self.entries: dict[str, dict[str, Any]] = {}
        if self.path.exists():
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            for entry in payload.get("entries", []):
                self.entries[str(entry["id"])] = dict(entry)

    def upsert(
        self,
        scored_papers: Iterable[ScoredPaper],
        start_date: date,
        end_date: date,
        *,
        as_of: date | None = None,
    ) -> QueueUpdate:
        """Upsert ranked candidates, preserving prior decisions and notes."""

        observed = as_of or date.today()
        added = updated = 0
        for rank, scored in enumerate(scored_papers, start=1):
            paper = scored.paper
            identity = paper_identity(paper)
            previous = self.entries.get(identity)
            entry = {
                "id": identity,
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": list(paper.authors),
                "source": paper.source,
                "url": paper.url,
                "online_date": paper_online_date(paper).isoformat()
                if paper_online_date(paper)
                else None,
                "score": round(scored.score, 6),
                "rank": rank,
                "reasons": list(scored.reasons),
                "assessment": asdict(scored.relevance) if scored.relevance else None,
                "status": previous.get("status", "queued") if previous else "queued",
                "notes": previous.get("notes", "") if previous else "",
                "first_seen": previous.get("first_seen", observed.isoformat())
                if previous
                else observed.isoformat(),
                "last_seen": observed.isoformat(),
                "window": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            }
            self.entries[identity] = entry
            if previous is None:
                added += 1
            else:
                updated += 1
        return QueueUpdate(added=added, updated=updated, total=len(self.entries))

    def save(self) -> Path:
        """Write the queue in stable score order."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        entries = sorted(
            self.entries.values(),
            key=lambda entry: (-float(entry.get("score", 0.0)), str(entry.get("title", ""))),
        )
        payload = {
            "schema_version": 1,
            "statuses": list(QUEUE_STATUSES),
            "entries": entries,
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return self.path


def _coerce_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not value:
        return None
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _metadata_richness(paper: Paper) -> tuple[int, int, int, int]:
    return (
        bool(paper.abstract),
        len(paper.abstract),
        len(paper.authors),
        len(paper.raw),
    )
