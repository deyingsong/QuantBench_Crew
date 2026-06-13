"""Shared plumbing for source-grounded Reader component extraction."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from quantbench_crew.llm import llm_for_agent
from quantbench_crew.models import EvidenceLink, PaperAnalysis
from quantbench_crew.prompts import load_prompt
from quantbench_crew.skills.base import RunContext, SkillResult
from quantbench_crew.skills.validation import extract_json_object, validate

FULLTEXT_EXCERPT_CHARS = 12000
EVIDENCE_SCHEMA: dict[str, Any] = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["field", "quote"],
        "properties": {
            "field": {"type": "string"},
            "quote": {"type": "string"},
        },
    },
}


def build_component_prompt(
    prompt_name: str, analysis: PaperAnalysis, full_text: str = ""
) -> str:
    """Build a stable prompt from known analysis plus available full text."""

    prompt = load_prompt(prompt_name).format(
        title=analysis.paper.title,
        abstract=analysis.paper.abstract,
        research_question=analysis.research_question,
        proposed_method=analysis.proposed_method,
        assumptions=", ".join(analysis.assumptions),
        datasets=", ".join(analysis.datasets),
        metrics=", ".join(analysis.metrics),
        limitations=", ".join(analysis.limitations),
    )
    if full_text:
        prompt += "\n\nFull-text excerpts (authoritative over metadata):\n"
        prompt += full_text[:FULLTEXT_EXCERPT_CHARS]
    return prompt


def run_component_extraction(
    ctx: RunContext,
    *,
    analysis: PaperAnalysis,
    full_text: str,
    skill_name: str,
    payload_key: str,
    prompt_name: str,
    system_prompt: str,
    schema: dict[str, Any],
    fallback: Callable[[PaperAnalysis, str], dict[str, Any]],
) -> SkillResult:
    """Run one schema-validated Reader extraction with an offline fallback."""

    notes: list[str] = []
    data: dict[str, Any] | None = None
    source = "metadata_fallback"
    client = llm_for_agent(ctx.llm, "quant_reader")

    if client is None:
        notes.append(
            f"no LLM configured for quant_reader; using deterministic {skill_name} fallback"
        )
    else:
        prompt = build_component_prompt(prompt_name, analysis, full_text)
        try:
            response = client.complete(prompt, system=system_prompt)
            candidate = extract_json_object(response.text)
            errors = validate(candidate, schema)
            if errors:
                notes.append("LLM output failed schema validation: " + "; ".join(errors[:5]))
            else:
                data = dict(candidate)
                data["confidence"] = _clamp_confidence(data.get("confidence"))
                data["evidence"] = verified_evidence(
                    data.get("evidence", []), source_text(analysis, full_text), full_text
                )
                source = "llm_fulltext" if full_text else "llm"
                if not data["evidence"]:
                    notes.append("LLM evidence quotes could not be verified against supplied text")
        except Exception as exc:  # boundary: fall back and record why
            notes.append(f"LLM extraction failed: {exc!r}")

    if data is None:
        data = fallback(analysis, full_text)
        data["confidence"] = _clamp_confidence(data.get("confidence"))
        data["evidence"] = verified_evidence(
            data.get("evidence", []), source_text(analysis, full_text), full_text
        )
        source = "fulltext_fallback" if full_text else "metadata_fallback"
        notes.append(f"deterministic {skill_name} fallback produced the assessment")

    result = SkillResult(
        skill=skill_name,
        status="ok",
        payload={
            payload_key: data,
            "confidence": data["confidence"],
            "source": source,
        },
        notes=tuple(notes),
    )
    ctx.manifest.record_skill(result)
    return result


def source_text(analysis: PaperAnalysis, full_text: str = "") -> str:
    """Return the strongest available paper-derived text signal."""

    metadata = f"{analysis.paper.title}. {analysis.paper.abstract}"
    return f"{metadata}\n{full_text}" if full_text else metadata


def sentences_matching(
    text: str, markers: tuple[str, ...], limit: int = 4
) -> list[str]:
    """Return unique sentences containing any marker, preserving order."""

    matches = []
    for sentence in _sentences(text):
        lowered = sentence.lower()
        if any(marker in lowered for marker in markers):
            matches.append(sentence)
    return unique_strings(matches)[:limit]


def evidence_items(field: str, values: list[str] | tuple[str, ...]) -> list[dict[str, str]]:
    """Create JSON-shaped evidence items from extracted source sentences."""

    return [{"field": field, "quote": value} for value in values if value]


def evidence_links(items: list[dict[str, Any]]) -> tuple[EvidenceLink, ...]:
    """Rebuild typed EvidenceLinks from normalized payload evidence."""

    return tuple(
        EvidenceLink(
            kind=str(item.get("kind", "paper_quote")),
            reference=str(item.get("reference", "")),
            detail=str(item.get("detail", "")),
        )
        for item in items
    )


def string_tuple(value: Any) -> tuple[str, ...]:
    """Normalize a JSON string/list into a tuple of non-empty strings."""

    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(unique_strings([str(item) for item in value]))


def substantive_strings(values: tuple[str, ...]) -> list[str]:
    """Remove pipeline-status placeholders that are not claims by the paper."""

    placeholders = (
        "requires human review",
        "not identified from metadata",
        "metadata-only extraction",
        "paperqa2 answer",
        "paperqa2 extraction",
    )
    return [
        value
        for value in values
        if not any(marker in value.casefold() for marker in placeholders)
    ]


def verified_evidence(
    items: Any, text: str, full_text: str = ""
) -> list[dict[str, str]]:
    """Keep only evidence quotes that occur in the supplied paper text."""

    if not isinstance(items, list):
        return []
    normalized_text = _normalize_for_match(text)
    normalized_full_text = _normalize_for_match(full_text)
    verified: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        quote = " ".join(str(item.get("quote", "")).split())
        field = str(item.get("field", "")).strip()
        if quote and _normalize_for_match(quote) in normalized_text:
            reference = (
                "full_text"
                if full_text and _normalize_for_match(quote) in normalized_full_text
                else "abstract"
            )
            verified.append(
                {
                    "kind": "paper_quote",
                    "reference": f"{reference}:{field}" if field else reference,
                    "detail": quote,
                }
            )
    return verified


def unique_strings(values: list[str]) -> list[str]:
    """Deduplicate stripped strings case-insensitively, preserving order."""

    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        cleaned = " ".join(value.split()).strip()
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            unique.append(cleaned)
    return unique


def _sentences(text: str) -> list[str]:
    return unique_strings(re.split(r"(?<=[.!?])\s+|\n+", text))


def _normalize_for_match(text: str) -> str:
    return " ".join(text.casefold().split())


def _clamp_confidence(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0
