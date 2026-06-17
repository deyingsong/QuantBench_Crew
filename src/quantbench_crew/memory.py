"""Governed persistent memory for QuantBench Crew.

The SQLite database is an operational index and learning ledger. Run artifacts
and manifests remain the canonical evidence. Only approved memories are
eligible for recall, and every recalled memory is recorded in the run
manifest so its influence on a run remains auditable.
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from quantbench_crew.artifacts import canonical_json, stable_hash

SCHEMA_VERSION = 1
DEFAULT_MEMORY_PATH = Path("data/quantbench_memory.sqlite3")
DEFAULT_ARCHIVE_DIR = Path("data/archive")
ACTIVE_MEMORY_STATUSES = ("approved",)
PROTECTED_MEMORY_KINDS = ("procedural", "prospective")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | date | None = None) -> str:
    moment = value or _utc_now()
    if isinstance(moment, date) and not isinstance(moment, datetime):
        return datetime.combine(moment, datetime.min.time(), tzinfo=timezone.utc).isoformat()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat()


def _json(value: Any) -> str:
    return canonical_json(value)


def _loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


@dataclass(frozen=True)
class MemoryRecord:
    memory_id: str
    kind: str
    scope: str
    scope_key: str
    content: str
    status: str
    importance: float
    tags: tuple[str, ...]
    source_type: str
    source_id: str
    created_at: str
    updated_at: str
    supersedes_id: str = ""

    @property
    def content_hash(self) -> str:
        return stable_hash(
            {
                "kind": self.kind,
                "scope": self.scope,
                "scope_key": self.scope_key,
                "content": self.content,
                "status": self.status,
                "tags": self.tags,
            }
        )


@dataclass(frozen=True)
class FeedbackRecord:
    feedback_id: str
    run_id: str
    paper_slug: str
    source_path: str
    report_hash: str
    raw_text: str
    category: str
    scope: str
    scope_key: str
    target_agent: str
    status: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ConsolidationResult:
    month: str
    events_considered: int
    memories_considered: int
    duplicates_superseded: int
    digest_memory_id: str


@dataclass(frozen=True)
class ArchiveResult:
    cutoff: str
    archive_path: str
    events_archived: int
    memories_archived: int


@runtime_checkable
class MemoryStore(Protocol):
    def remember(self, content: str, **metadata: Any) -> MemoryRecord:
        ...

    def retrieve(
        self, *, agent: str, paper_slug: str = "", query: str = "", limit: int = 8
    ) -> tuple[MemoryRecord, ...]:
        ...

    def record_event(
        self, event_type: str, payload: Mapping[str, Any], **metadata: Any
    ) -> str:
        ...


class SQLiteMemoryStore:
    """Local, dependency-free memory backend with provenance and lifecycle rules."""

    def __init__(self, path: str | Path = DEFAULT_MEMORY_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    paper_slug TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    config_hash TEXT NOT NULL,
                    content_hash TEXT,
                    status TEXT NOT NULL DEFAULT 'running',
                    summary_json TEXT NOT NULL DEFAULT '{}'
                );

                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_key TEXT NOT NULL UNIQUE,
                    run_id TEXT,
                    agent TEXT NOT NULL DEFAULT '',
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id)
                );

                CREATE INDEX IF NOT EXISTS idx_events_created
                    ON events(created_at);
                CREATE INDEX IF NOT EXISTS idx_events_run
                    ON events(run_id);

                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    scope_key TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL,
                    status TEXT NOT NULL,
                    importance REAL NOT NULL DEFAULT 0.5,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    source_type TEXT NOT NULL DEFAULT '',
                    source_id TEXT NOT NULL DEFAULT '',
                    provenance_json TEXT NOT NULL DEFAULT '{}',
                    supersedes_id TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_accessed_at TEXT,
                    archived_at TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_memories_recall
                    ON memories(status, scope, scope_key, archived_at);
                CREATE INDEX IF NOT EXISTS idx_memories_updated
                    ON memories(updated_at);

                CREATE TABLE IF NOT EXISTS memory_sources (
                    memory_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY(memory_id, source_type, source_id),
                    FOREIGN KEY(memory_id) REFERENCES memories(memory_id)
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    dedupe_key TEXT NOT NULL UNIQUE,
                    run_id TEXT NOT NULL DEFAULT '',
                    paper_slug TEXT NOT NULL DEFAULT '',
                    source_path TEXT NOT NULL,
                    report_hash TEXT NOT NULL,
                    raw_text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    scope_key TEXT NOT NULL DEFAULT '',
                    target_agent TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'new',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS change_proposals (
                    proposal_id TEXT PRIMARY KEY,
                    feedback_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    proposed_value TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'proposed',
                    evaluation_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(feedback_id) REFERENCES feedback(feedback_id)
                );

                CREATE TABLE IF NOT EXISTS consolidation_runs (
                    consolidation_id TEXT PRIMARY KEY,
                    month TEXT NOT NULL UNIQUE,
                    summary_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS archive_index (
                    archive_id TEXT PRIMARY KEY,
                    cutoff TEXT NOT NULL,
                    archive_path TEXT NOT NULL,
                    events_archived INTEGER NOT NULL,
                    memories_archived INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            try:
                connection.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
                    USING fts5(memory_id UNINDEXED, content, tags)
                    """
                )
            except sqlite3.OperationalError:
                # Some minimal SQLite builds omit FTS5. Retrieval retains a
                # deterministic token-overlap fallback.
                pass
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def record_run_started(self, manifest: Any) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs(
                    run_id, paper_slug, started_at, config_hash, status
                ) VALUES (?, ?, ?, ?, 'running')
                ON CONFLICT(run_id) DO UPDATE SET
                    paper_slug=excluded.paper_slug,
                    started_at=excluded.started_at,
                    config_hash=excluded.config_hash,
                    status='running'
                """,
                (
                    manifest.run_id,
                    manifest.paper_slug,
                    _iso(manifest.started_at),
                    manifest.config_hash,
                ),
            )

    def record_manifest(self, manifest: Any, *, status: str = "completed") -> None:
        summary = {
            "skill_count": len(manifest.skill_results),
            "llm_call_count": len(manifest.llm_calls),
            "artifact_count": len(manifest.artifacts),
            "memory_reads": list(getattr(manifest, "memory_reads", [])),
            "memory_writes": list(getattr(manifest, "memory_writes", [])),
        }
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs(
                    run_id, paper_slug, started_at, completed_at, config_hash,
                    content_hash, status, summary_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    completed_at=excluded.completed_at,
                    content_hash=excluded.content_hash,
                    status=excluded.status,
                    summary_json=excluded.summary_json
                """,
                (
                    manifest.run_id,
                    manifest.paper_slug,
                    _iso(manifest.started_at),
                    _iso(),
                    manifest.config_hash,
                    manifest.content_hash(),
                    status,
                    _json(summary),
                ),
            )
        for index, result in enumerate(manifest.skill_results):
            self.record_event(
                "skill_invocation",
                asdict(result),
                run_id=manifest.run_id,
                agent=_agent_for_skill(result.skill),
                event_key=f"{manifest.run_id}:skill:{index}:{result.skill}",
                created_at=manifest.started_at,
            )
        for index, call in enumerate(manifest.llm_calls):
            self.record_event(
                "llm_call",
                call,
                run_id=manifest.run_id,
                agent=str(call.get("agent", "")),
                event_key=f"{manifest.run_id}:llm:{index}",
                created_at=manifest.started_at,
            )
        self.record_event(
            "run_completed",
            summary,
            run_id=manifest.run_id,
            event_key=f"{manifest.run_id}:completed",
        )

    def record_event(
        self,
        event_type: str,
        payload: Mapping[str, Any],
        *,
        run_id: str = "",
        agent: str = "",
        event_key: str = "",
        created_at: datetime | date | None = None,
    ) -> str:
        payload_json = _json(dict(payload))
        key = event_key or stable_hash(
            {
                "run_id": run_id,
                "agent": agent,
                "event_type": event_type,
                "payload": payload,
            }
        )
        event_id = f"evt-{stable_hash(key)[:24]}"
        with self._connect() as connection:
            linked_run_id = run_id
            if linked_run_id:
                exists = connection.execute(
                    "SELECT 1 FROM runs WHERE run_id = ?", (linked_run_id,)
                ).fetchone()
                if exists is None:
                    linked_run_id = ""
            connection.execute(
                """
                INSERT OR IGNORE INTO events(
                    event_id, event_key, run_id, agent, event_type,
                    payload_json, created_at
                ) VALUES (?, ?, NULLIF(?, ''), ?, ?, ?, ?)
                """,
                (
                    event_id,
                    key,
                    linked_run_id,
                    agent,
                    event_type,
                    payload_json,
                    _iso(created_at),
                ),
            )
        return event_id

    def remember(
        self,
        content: str,
        *,
        kind: str = "semantic",
        scope: str = "global",
        scope_key: str = "",
        status: str = "approved",
        importance: float = 0.5,
        tags: Iterable[str] = (),
        source_type: str = "",
        source_id: str = "",
        provenance: Mapping[str, Any] | None = None,
        supersedes_id: str = "",
        memory_id: str = "",
    ) -> MemoryRecord:
        normalized = content.strip()
        if not normalized:
            raise ValueError("memory content must not be empty")
        tag_tuple = tuple(dict.fromkeys(str(tag).strip() for tag in tags if str(tag).strip()))
        identity = memory_id or (
            "mem-"
            + stable_hash(
                {
                    "content": normalized,
                    "kind": kind,
                    "scope": scope,
                    "scope_key": scope_key,
                    "source_type": source_type,
                    "source_id": source_id,
                }
            )[:24]
        )
        now = _iso()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories(
                    memory_id, kind, scope, scope_key, content, status,
                    importance, tags_json, source_type, source_id,
                    provenance_json, supersedes_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    kind=excluded.kind,
                    scope=excluded.scope,
                    scope_key=excluded.scope_key,
                    content=excluded.content,
                    status=excluded.status,
                    importance=excluded.importance,
                    tags_json=excluded.tags_json,
                    provenance_json=excluded.provenance_json,
                    supersedes_id=excluded.supersedes_id,
                    updated_at=excluded.updated_at,
                    archived_at=NULL
                """,
                (
                    identity,
                    kind,
                    scope,
                    scope_key,
                    normalized,
                    status,
                    max(0.0, min(1.0, float(importance))),
                    _json(tag_tuple),
                    source_type,
                    source_id,
                    _json(dict(provenance or {})),
                    supersedes_id,
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO memory_sources(
                    memory_id, source_type, source_id, detail
                ) VALUES (?, ?, ?, ?)
                """,
                (identity, source_type, source_id, _json(dict(provenance or {}))),
            )
            self._sync_fts(connection, identity, normalized, tag_tuple)
            row = connection.execute(
                "SELECT * FROM memories WHERE memory_id = ?", (identity,)
            ).fetchone()
        return _memory_from_row(row)

    def _sync_fts(
        self,
        connection: sqlite3.Connection,
        memory_id: str,
        content: str,
        tags: Iterable[str],
    ) -> None:
        try:
            connection.execute("DELETE FROM memory_fts WHERE memory_id = ?", (memory_id,))
            connection.execute(
                "INSERT INTO memory_fts(memory_id, content, tags) VALUES (?, ?, ?)",
                (memory_id, content, " ".join(tags)),
            )
        except sqlite3.OperationalError:
            pass

    def retrieve(
        self,
        *,
        agent: str,
        paper_slug: str = "",
        query: str = "",
        limit: int = 8,
    ) -> tuple[MemoryRecord, ...]:
        if limit <= 0:
            return ()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM memories
                WHERE status = 'approved'
                  AND archived_at IS NULL
                  AND (
                    scope = 'global'
                    OR (scope = 'agent' AND scope_key = ?)
                    OR (scope = 'paper' AND scope_key = ?)
                    OR (scope = 'agent_paper' AND scope_key = ?)
                  )
                """,
                (agent, paper_slug, f"{agent}:{paper_slug}"),
            ).fetchall()

            tokens = _tokens(query)
            ranked = sorted(
                (_memory_from_row(row) for row in rows),
                key=lambda item: _memory_rank(item, agent, paper_slug, tokens),
                reverse=True,
            )[:limit]
            if ranked:
                now = _iso()
                connection.executemany(
                    "UPDATE memories SET last_accessed_at = ? WHERE memory_id = ?",
                    [(now, item.memory_id) for item in ranked],
                )
        return tuple(ranked)

    def memory(self, memory_id: str) -> MemoryRecord:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM memories WHERE memory_id = ?", (memory_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown memory id: {memory_id}")
        return _memory_from_row(row)

    def set_memory_status(self, memory_id: str, status: str) -> MemoryRecord:
        if status not in {"proposed", "approved", "rejected", "superseded"}:
            raise ValueError(f"unsupported memory status: {status}")
        self.memory(memory_id)
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE memories SET status=?, updated_at=?, archived_at=NULL
                WHERE memory_id=?
                """,
                (status, _iso(), memory_id),
            )
            row = connection.execute(
                "SELECT * FROM memories WHERE memory_id = ?", (memory_id,)
            ).fetchone()
        return _memory_from_row(row)

    def ingest_feedback(
        self,
        *,
        raw_text: str,
        source_path: str,
        report_hash: str,
        run_id: str = "",
        paper_slug: str = "",
        category: str = "process_guidance",
        scope: str = "paper",
        scope_key: str = "",
        target_agent: str = "",
        action_type: str = "add_guidance",
    ) -> tuple[FeedbackRecord, bool]:
        text = raw_text.strip()
        if not text:
            raise ValueError("human proofreading notes are empty")
        resolved_scope_key = scope_key or (
            target_agent if scope == "agent" else paper_slug if scope == "paper" else ""
        )
        dedupe_key = stable_hash(
            {
                "report_hash": report_hash,
                "raw_text": text,
                "run_id": run_id,
                "paper_slug": paper_slug,
            }
        )
        feedback_id = f"fb-{dedupe_key[:24]}"
        proposal_id = f"chg-{stable_hash({'feedback_id': feedback_id, 'action': action_type})[:24]}"
        now = _iso()
        created = False
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO feedback(
                    feedback_id, dedupe_key, run_id, paper_slug, source_path,
                    report_hash, raw_text, category, scope, scope_key,
                    target_agent, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposed', ?, ?)
                """,
                (
                    feedback_id,
                    dedupe_key,
                    run_id,
                    paper_slug,
                    source_path,
                    report_hash,
                    text,
                    category,
                    scope,
                    resolved_scope_key,
                    target_agent,
                    now,
                    now,
                ),
            )
            created = cursor.rowcount > 0
            connection.execute(
                """
                INSERT OR IGNORE INTO change_proposals(
                    proposal_id, feedback_id, action_type, target,
                    proposed_value, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'proposed', ?, ?)
                """,
                (
                    proposal_id,
                    feedback_id,
                    action_type,
                    f"{scope}:{resolved_scope_key}",
                    text,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM feedback WHERE dedupe_key = ?", (dedupe_key,)
            ).fetchone()
        return _feedback_from_row(row), created

    def feedback(self, feedback_id: str) -> FeedbackRecord:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM feedback WHERE feedback_id = ?", (feedback_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown feedback id: {feedback_id}")
        return _feedback_from_row(row)

    def list_feedback(self, *, status: str = "") -> tuple[FeedbackRecord, ...]:
        with self._connect() as connection:
            if status:
                rows = connection.execute(
                    "SELECT * FROM feedback WHERE status = ? ORDER BY created_at",
                    (status,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM feedback ORDER BY created_at"
                ).fetchall()
        return tuple(_feedback_from_row(row) for row in rows)

    def approve_feedback(
        self,
        feedback_id: str,
        *,
        reviewer: str = "",
        importance: float = 0.8,
    ) -> MemoryRecord:
        feedback = self.feedback(feedback_id)
        kind = _memory_kind_for_feedback(feedback.category)
        memory = self.remember(
            feedback.raw_text,
            kind=kind,
            scope=feedback.scope,
            scope_key=feedback.scope_key,
            status="approved",
            importance=importance,
            tags=("human_expert", feedback.category, feedback.target_agent),
            source_type="human_feedback",
            source_id=feedback.feedback_id,
            provenance={
                "run_id": feedback.run_id,
                "paper_slug": feedback.paper_slug,
                "source_path": feedback.source_path,
                "reviewer": reviewer,
            },
        )
        now = _iso()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE feedback SET status='approved', updated_at=?
                WHERE feedback_id=?
                """,
                (now, feedback_id),
            )
            connection.execute(
                """
                UPDATE change_proposals
                SET status='approved', updated_at=? WHERE feedback_id=?
                """,
                (now, feedback_id),
            )
        self.record_event(
            "feedback_approved",
            {
                "feedback_id": feedback_id,
                "memory_id": memory.memory_id,
                "reviewer": reviewer,
            },
            run_id=feedback.run_id,
            agent=feedback.target_agent,
        )
        return memory

    def reject_feedback(self, feedback_id: str, *, reviewer: str = "") -> None:
        self.feedback(feedback_id)
        now = _iso()
        with self._connect() as connection:
            connection.execute(
                "UPDATE feedback SET status='rejected', updated_at=? WHERE feedback_id=?",
                (now, feedback_id),
            )
            connection.execute(
                """
                UPDATE change_proposals
                SET status='rejected', evaluation_json=?, updated_at=?
                WHERE feedback_id=?
                """,
                (_json({"reviewer": reviewer}), now, feedback_id),
            )

    def consolidate_month(self, month: str) -> ConsolidationResult:
        start = date.fromisoformat(f"{month}-01")
        if start.month == 12:
            end = date(start.year + 1, 1, 1)
        else:
            end = date(start.year, start.month + 1, 1)
        start_iso = _iso(start)
        end_iso = _iso(end)
        with self._connect() as connection:
            event_rows = connection.execute(
                """
                SELECT event_type, agent, payload_json FROM events
                WHERE created_at >= ? AND created_at < ?
                """,
                (start_iso, end_iso),
            ).fetchall()
            memory_rows = connection.execute(
                """
                SELECT * FROM memories
                WHERE created_at >= ? AND created_at < ? AND archived_at IS NULL
                """,
                (start_iso, end_iso),
            ).fetchall()

        memories = [_memory_from_row(row) for row in memory_rows]
        duplicates = self._supersede_exact_duplicates(memories)
        event_counts = Counter(str(row["event_type"]) for row in event_rows)
        agent_counts = Counter(str(row["agent"]) for row in event_rows if row["agent"])
        failed_skills: Counter[str] = Counter()
        for row in event_rows:
            if row["event_type"] != "skill_invocation":
                continue
            payload = _loads(str(row["payload_json"]), {})
            if payload.get("status") == "failed":
                failed_skills[str(payload.get("skill", "unknown"))] += 1

        digest = "\n".join(
            [
                f"Monthly QuantBench memory consolidation for {month}.",
                f"Events: {dict(sorted(event_counts.items()))}.",
                f"Agent activity: {dict(sorted(agent_counts.items()))}.",
                f"Failed skills: {dict(sorted(failed_skills.items())) or {}}.",
                f"Memories reviewed: {len(memories)}; exact duplicates superseded: {duplicates}.",
                "This digest is descriptive. It does not activate new procedural guidance.",
            ]
        )
        digest_memory = self.remember(
            digest,
            kind="semantic",
            scope="global",
            status="consolidated",
            importance=0.45,
            tags=("monthly_consolidation", month),
            source_type="consolidation",
            source_id=month,
        )
        summary = {
            "month": month,
            "event_counts": dict(event_counts),
            "agent_counts": dict(agent_counts),
            "failed_skills": dict(failed_skills),
            "memories_considered": len(memories),
            "duplicates_superseded": duplicates,
            "digest_memory_id": digest_memory.memory_id,
        }
        consolidation_id = f"con-{stable_hash(summary)[:24]}"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO consolidation_runs(
                    consolidation_id, month, summary_json, created_at
                ) VALUES (?, ?, ?, ?)
                ON CONFLICT(month) DO UPDATE SET
                    consolidation_id=excluded.consolidation_id,
                    summary_json=excluded.summary_json,
                    created_at=excluded.created_at
                """,
                (consolidation_id, month, _json(summary), _iso()),
            )
        return ConsolidationResult(
            month=month,
            events_considered=len(event_rows),
            memories_considered=len(memories),
            duplicates_superseded=duplicates,
            digest_memory_id=digest_memory.memory_id,
        )

    def _supersede_exact_duplicates(self, memories: Iterable[MemoryRecord]) -> int:
        grouped: dict[tuple[str, str, str, str], list[MemoryRecord]] = {}
        for memory in memories:
            key = (memory.kind, memory.scope, memory.scope_key, memory.content.strip().lower())
            grouped.setdefault(key, []).append(memory)
        count = 0
        with self._connect() as connection:
            for group in grouped.values():
                if len(group) < 2:
                    continue
                group.sort(key=lambda item: item.created_at)
                keeper = group[0]
                for duplicate in group[1:]:
                    connection.execute(
                        """
                        UPDATE memories
                        SET status='superseded', supersedes_id=?, updated_at=?
                        WHERE memory_id=?
                        """,
                        (keeper.memory_id, _iso(), duplicate.memory_id),
                    )
                    count += 1
        return count

    def archive_older_than(
        self,
        days: int = 90,
        *,
        archive_dir: str | Path = DEFAULT_ARCHIVE_DIR,
        now: datetime | None = None,
    ) -> ArchiveResult:
        if days < 1:
            raise ValueError("archive age must be at least one day")
        moment = now or _utc_now()
        cutoff = moment - timedelta(days=days)
        cutoff_iso = _iso(cutoff)
        destination_dir = Path(archive_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        quarter = ((cutoff.month - 1) // 3) + 1
        archive_path = destination_dir / f"quantbench-{cutoff.year}-q{quarter}.sqlite3"

        with self._connect() as connection:
            event_rows = connection.execute(
                "SELECT * FROM events WHERE created_at < ?", (cutoff_iso,)
            ).fetchall()
            memory_rows = connection.execute(
                """
                SELECT * FROM memories
                WHERE updated_at < ?
                  AND archived_at IS NULL
                  AND (
                    status IN ('superseded', 'rejected', 'proposed')
                    OR (status = 'approved' AND kind = 'episodic')
                    OR (status != 'approved' AND kind NOT IN ('procedural', 'prospective'))
                  )
                """,
                (cutoff_iso,),
            ).fetchall()

        self._write_archive(archive_path, event_rows, memory_rows)
        now_iso = _iso(moment)
        with self._connect() as connection:
            if event_rows:
                connection.executemany(
                    "DELETE FROM events WHERE event_id = ?",
                    [(row["event_id"],) for row in event_rows],
                )
            if memory_rows:
                connection.executemany(
                    "UPDATE memories SET archived_at = ? WHERE memory_id = ?",
                    [(now_iso, row["memory_id"]) for row in memory_rows],
                )
            result_payload = {
                "cutoff": cutoff_iso,
                "archive_path": str(archive_path),
                "events_archived": len(event_rows),
                "memories_archived": len(memory_rows),
            }
            archive_id = f"arc-{stable_hash(result_payload)[:24]}"
            connection.execute(
                """
                INSERT OR REPLACE INTO archive_index(
                    archive_id, cutoff, archive_path, events_archived,
                    memories_archived, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    archive_id,
                    cutoff_iso,
                    str(archive_path),
                    len(event_rows),
                    len(memory_rows),
                    now_iso,
                ),
            )
        return ArchiveResult(
            cutoff=cutoff_iso,
            archive_path=str(archive_path),
            events_archived=len(event_rows),
            memories_archived=len(memory_rows),
        )

    def _write_archive(
        self,
        path: Path,
        event_rows: Iterable[sqlite3.Row],
        memory_rows: Iterable[sqlite3.Row],
    ) -> None:
        with sqlite3.connect(path) as archive:
            archive.executescript(
                """
                CREATE TABLE IF NOT EXISTS events_archive (
                    event_id TEXT PRIMARY KEY,
                    event_key TEXT,
                    run_id TEXT,
                    agent TEXT,
                    event_type TEXT,
                    payload_json TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS memories_archive (
                    memory_id TEXT PRIMARY KEY,
                    kind TEXT,
                    scope TEXT,
                    scope_key TEXT,
                    content TEXT,
                    status TEXT,
                    importance REAL,
                    tags_json TEXT,
                    source_type TEXT,
                    source_id TEXT,
                    provenance_json TEXT,
                    supersedes_id TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    last_accessed_at TEXT,
                    archived_at TEXT
                );
                """
            )
            archive.executemany(
                """
                INSERT OR IGNORE INTO events_archive VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [tuple(row) for row in event_rows],
            )
            archive.executemany(
                """
                INSERT OR IGNORE INTO memories_archive VALUES(
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                [tuple(row) for row in memory_rows],
            )

    def inspect(self) -> dict[str, Any]:
        with self._connect() as connection:
            runs = connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            events = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            memories = dict(
                connection.execute(
                    "SELECT status, COUNT(*) FROM memories GROUP BY status"
                ).fetchall()
            )
            feedback = dict(
                connection.execute(
                    "SELECT status, COUNT(*) FROM feedback GROUP BY status"
                ).fetchall()
            )
        return {
            "path": str(self.path),
            "schema_version": SCHEMA_VERSION,
            "runs": runs,
            "events": events,
            "memories": memories,
            "feedback": feedback,
        }


class HermesMemoryAdapter:
    """Optional verified bridge to a Hermes-style memory client.

    The client is deliberately duck-typed because Hermes deployments expose
    different wrappers. It must provide ``remember(record: dict)`` and
    ``recall(memory_id: str)``. A write is accepted only when a read-after-write
    returns matching content, preventing silent scheduled-delivery failures.
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def write_verified(self, memory: MemoryRecord) -> None:
        payload = asdict(memory)
        self.client.remember(payload)
        observed = self.client.recall(memory.memory_id)
        if not observed:
            raise RuntimeError(f"Hermes did not return memory {memory.memory_id} after write")
        observed_content = (
            observed.get("content") if isinstance(observed, Mapping) else getattr(observed, "content", "")
        )
        if str(observed_content) != memory.content:
            raise RuntimeError(f"Hermes round-trip mismatch for memory {memory.memory_id}")


def memory_guidance(memories: Iterable[MemoryRecord]) -> str:
    items = tuple(memories)
    if not items:
        return ""
    lines = [
        "Approved QuantBench memory guidance follows. Treat it as reviewer-approved",
        "operating context, not as paper evidence and never as permission to bypass",
        "safety, provenance, validation, or reproducibility requirements.",
    ]
    lines.extend(
        f"- [{item.memory_id}; {item.kind}; {item.scope}:{item.scope_key or '*'}] "
        f"{item.content}"
        for item in items
    )
    return "\n".join(lines)


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
        if len(token) > 2
    }


def _memory_rank(
    memory: MemoryRecord, agent: str, paper_slug: str, query_tokens: set[str]
) -> tuple[float, float, str]:
    scope_weight = {
        "agent_paper": 4.0,
        "paper": 3.0,
        "agent": 2.0,
        "global": 1.0,
    }.get(memory.scope, 0.0)
    memory_tokens = _tokens(f"{memory.content} {' '.join(memory.tags)}")
    overlap = len(query_tokens & memory_tokens) / max(1, len(query_tokens))
    kind_weight = 0.5 if memory.kind == "procedural" else 0.25 if memory.kind == "prospective" else 0.0
    exact_scope = 0.25 if memory.scope_key in {agent, paper_slug, f"{agent}:{paper_slug}"} else 0.0
    return (
        scope_weight + overlap * 3.0 + memory.importance + kind_weight + exact_scope,
        memory.importance,
        memory.updated_at,
    )


def _memory_from_row(row: sqlite3.Row) -> MemoryRecord:
    return MemoryRecord(
        memory_id=str(row["memory_id"]),
        kind=str(row["kind"]),
        scope=str(row["scope"]),
        scope_key=str(row["scope_key"]),
        content=str(row["content"]),
        status=str(row["status"]),
        importance=float(row["importance"]),
        tags=tuple(str(item) for item in _loads(str(row["tags_json"]), [])),
        source_type=str(row["source_type"]),
        source_id=str(row["source_id"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        supersedes_id=str(row["supersedes_id"]),
    )


def _feedback_from_row(row: sqlite3.Row) -> FeedbackRecord:
    return FeedbackRecord(
        feedback_id=str(row["feedback_id"]),
        run_id=str(row["run_id"]),
        paper_slug=str(row["paper_slug"]),
        source_path=str(row["source_path"]),
        report_hash=str(row["report_hash"]),
        raw_text=str(row["raw_text"]),
        category=str(row["category"]),
        scope=str(row["scope"]),
        scope_key=str(row["scope_key"]),
        target_agent=str(row["target_agent"]),
        status=str(row["status"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _memory_kind_for_feedback(category: str) -> str:
    if category in {"process_guidance", "bug"}:
        return "procedural"
    if category == "method_gap":
        return "prospective"
    return "semantic"


def _agent_for_skill(skill: str) -> str:
    if skill in {
        "arxiv_search",
        "charter_relevance",
        "relevance_scorer",
        "reproducibility_triage",
    }:
        return "quant_scout"
    if skill in {
        "pdf_acquisition",
        "question_identifier",
        "methodology_extractor",
        "empirical_spec_parser",
        "criticizer",
        "target_table_extraction",
        "method_spec_extraction",
        "red_flag_scan",
    }:
        return "quant_reader"
    if skill in {"code_generation", "metric_synthesis", "consult_reader"}:
        return "quant_coder"
    if skill in {
        "dataset_registry",
        "walk_forward",
        "strategy_evaluator",
        "robustness_auditor",
    }:
        return "quant_bench"
    if skill in {"rubric_verdict", "claims_vs_results_analyzer", "report_compiler"}:
        return "quant_reviewer"
    return ""
