"""Human proofreading-note preservation and governed feedback ingestion."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from quantbench_crew.artifacts import sha256_text
from quantbench_crew.memory import FeedbackRecord, SQLiteMemoryStore

FEEDBACK_HEADING = "## Human proofreading notes"
FEEDBACK_START = "<!-- quantbench:feedback:start -->"
FEEDBACK_END = "<!-- quantbench:feedback:end -->"
REPORT_META_PREFIX = "<!-- quantbench:report "
REPORT_META_SUFFIX = " -->"

AGENT_NAMES = (
    "quant_scout",
    "quant_reader",
    "quant_coder",
    "quant_bench",
    "quant_reviewer",
)


@dataclass(frozen=True)
class FeedbackClassification:
    category: str
    scope: str
    scope_key: str
    target_agent: str
    action_type: str


def ensure_feedback_section(
    markdown: str,
    *,
    run_id: str = "",
    paper_slug: str = "",
) -> str:
    """Normalize metadata and bounded feedback markers in a report."""

    text = markdown.rstrip()
    notes = extract_human_notes(text)
    text = _remove_metadata(text)
    text = _remove_feedback_section(text).rstrip()
    metadata = ""
    if run_id or paper_slug:
        metadata = (
            REPORT_META_PREFIX
            + json.dumps(
                {"run_id": run_id, "paper_slug": paper_slug},
                sort_keys=True,
                separators=(",", ":"),
            )
            + REPORT_META_SUFFIX
        )
        lines = text.splitlines()
        insert_at = 1 if lines and lines[0].startswith("# ") else 0
        lines[insert_at:insert_at] = ["", metadata]
        text = "\n".join(lines).rstrip()
    section = "\n".join(
        [
            FEEDBACK_HEADING,
            FEEDBACK_START,
            notes,
            FEEDBACK_END,
        ]
    )
    return f"{text}\n\n{section}\n"


def extract_human_notes(markdown: str) -> str:
    """Return only the editable contents of the proofreading section."""

    if FEEDBACK_START in markdown:
        after = markdown.split(FEEDBACK_START, 1)[1]
        body = after.split(FEEDBACK_END, 1)[0] if FEEDBACK_END in after else after
        return body.strip()
    match = re.search(
        r"(?im)^## Human proofreading notes\s*$",
        markdown,
    )
    if match is None:
        return ""
    return markdown[match.end():].strip()


def report_metadata(markdown: str) -> dict[str, str]:
    match = re.search(
        re.escape(REPORT_META_PREFIX) + r"(\{.*?\})" + re.escape(REPORT_META_SUFFIX),
        markdown,
    )
    if match is None:
        return {}
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}
    return {
        "run_id": str(payload.get("run_id", "")),
        "paper_slug": str(payload.get("paper_slug", "")),
    }


def merge_preserved_feedback(
    new_markdown: str,
    existing_markdown: str,
    *,
    run_id: str = "",
    paper_slug: str = "",
) -> str:
    """Carry prior notes into regenerated output without duplicating them."""

    existing_notes = extract_human_notes(existing_markdown)
    normalized = ensure_feedback_section(
        new_markdown, run_id=run_id, paper_slug=paper_slug
    )
    if not existing_notes:
        return normalized
    before, after = normalized.split(FEEDBACK_START, 1)
    _, suffix = after.split(FEEDBACK_END, 1)
    return f"{before}{FEEDBACK_START}\n{existing_notes}\n{FEEDBACK_END}{suffix}"


def classify_feedback(text: str, *, paper_slug: str = "") -> FeedbackClassification:
    """Deterministically classify notes before human approval."""

    lowered = text.lower()
    target_agent = next(
        (
            agent
            for agent in AGENT_NAMES
            if agent in lowered or agent.replace("_", " ") in lowered
        ),
        "",
    )
    if any(word in lowered for word in ("bug", "exception", "crash", "overwrite", "broken")):
        category = "bug"
    elif any(
        word in lowered
        for word in ("incorrect", "factually", "correction", "wrong value", "wrong date")
    ):
        category = "factual_correction"
    elif any(
        word in lowered
        for word in ("method", "assumption", "benchmark", "dataset", "look-ahead", "bias")
    ):
        category = "method_gap"
    elif any(word in lowered for word in ("wording", "grammar", "typo", "style", "format")):
        category = "style"
    else:
        category = "process_guidance"

    if target_agent:
        scope = "agent"
        scope_key = target_agent
    elif category in {"factual_correction", "method_gap", "style"} and paper_slug:
        scope = "paper"
        scope_key = paper_slug
    else:
        scope = "global"
        scope_key = ""
    action_type = {
        "bug": "create_regression_fix",
        "factual_correction": "correct_report_fact",
        "method_gap": "add_research_requirement",
        "style": "adjust_report_style",
        "process_guidance": "add_guidance",
    }[category]
    return FeedbackClassification(
        category=category,
        scope=scope,
        scope_key=scope_key,
        target_agent=target_agent,
        action_type=action_type,
    )


def ingest_report_feedback(
    report_path: str | Path,
    store: SQLiteMemoryStore,
    *,
    category: str = "",
    scope: str = "",
    scope_key: str = "",
    target_agent: str = "",
) -> tuple[FeedbackRecord, bool]:
    path = Path(report_path)
    markdown = path.read_text(encoding="utf-8")
    notes = extract_human_notes(markdown)
    if not notes:
        raise ValueError(f"no human proofreading notes found in {path}")
    metadata = report_metadata(markdown)
    if not metadata.get("run_id"):
        manifest_path = path.parent / "manifest.json"
        if manifest_path.exists():
            try:
                manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                metadata["run_id"] = str(manifest_payload.get("run_id", ""))
            except json.JSONDecodeError:
                pass
    paper_slug = metadata.get("paper_slug") or path.stem
    inferred = classify_feedback(notes, paper_slug=paper_slug)
    return store.ingest_feedback(
        raw_text=notes,
        source_path=str(path),
        report_hash=sha256_text(markdown),
        run_id=metadata.get("run_id", ""),
        paper_slug=paper_slug,
        category=category or inferred.category,
        scope=scope or inferred.scope,
        scope_key=scope_key or inferred.scope_key,
        target_agent=target_agent or inferred.target_agent,
        action_type=inferred.action_type,
    )


def _remove_feedback_section(markdown: str) -> str:
    if FEEDBACK_START in markdown:
        heading_index = markdown.rfind(FEEDBACK_HEADING, 0, markdown.index(FEEDBACK_START))
        start = heading_index if heading_index >= 0 else markdown.index(FEEDBACK_START)
        if FEEDBACK_END in markdown:
            end = markdown.index(FEEDBACK_END, start) + len(FEEDBACK_END)
        else:
            end = len(markdown)
        return markdown[:start] + markdown[end:]
    match = re.search(r"(?im)^## Human proofreading notes\s*$", markdown)
    return markdown[: match.start()] if match else markdown


def _remove_metadata(markdown: str) -> str:
    return re.sub(
        r"\n?" + re.escape(REPORT_META_PREFIX) + r"\{.*?\}" + re.escape(REPORT_META_SUFFIX),
        "",
        markdown,
        count=1,
    )
