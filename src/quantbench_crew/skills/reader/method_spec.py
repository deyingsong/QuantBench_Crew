"""MethodSpec extraction: LLM-backed with a deterministic metadata fallback.

The LLM path routes through the QB-02 seam, parses a JSON object from the
completion, and validates it against METHOD_SPEC_SCHEMA before anything
downstream sees it. Any failure on that path — no client configured, a
provider error, unparseable output, schema violations — downgrades to the
deterministic metadata heuristics with the reason recorded in the skill
notes, so the pipeline always yields a spec and the manifest always says
which path produced it.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from quantbench_crew.models import EvidenceLink, MethodSpec, Paper, PaperAnalysis
from quantbench_crew.prompts import load_prompt
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult
from quantbench_crew.skills.validation import extract_json_object, validate

PROMPT_NAME = "method_spec_extraction"
SYSTEM_PROMPT = (
    "You extract precise, implementable method specifications from "
    "quantitative finance papers. Answer with a single JSON object only."
)
FALLBACK_CONFIDENCE = 0.2

METHOD_SPEC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "universe",
        "frequency",
        "signal_definition",
        "portfolio_construction",
        "rebalance_frequency",
        "holding_period",
        "confidence",
    ],
    "properties": {
        "universe": {"type": "string"},
        "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
        "signal_definition": {"type": "string"},
        "portfolio_construction": {"type": "string"},
        "rebalance_frequency": {"type": "string"},
        "holding_period": {"type": "string"},
        "sample_start": {"type": ["string", "null"]},
        "sample_end": {"type": ["string", "null"]},
        "evaluation_protocol": {"type": "string"},
        "hyperparameters": {"type": "object"},
        "data_requirements": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
    },
}

_SAMPLE_PERIOD = re.compile(
    r"\b(19\d{2}|20\d{2})\s*(?:to|through|until|–|—|-)\s*(19\d{2}|20\d{2})\b"
)
_PAST_RETURN = re.compile(r"past\s+(\d+)[- ]month returns?", re.IGNORECASE)
_HOLDING = re.compile(r"for\s+(\d+)\s+(overlapping\s+)?months?", re.IGNORECASE)

_UNIVERSE_MARKERS = (
    "nyse",
    "amex",
    "nasdaq",
    "us common stocks",
    "s&p 500",
    "cryptocurrencies",
    "futures",
    "corporate bonds",
)
_CONSTRUCTION_MARKERS = (
    "decile",
    "quintile",
    "tercile",
    "equal-weighted",
    "value-weighted",
    "long-short",
    "winner-minus-loser",
    "winners-minus-losers",
)


FULLTEXT_CONFIDENCE_FLOOR = 0.7
FULLTEXT_EXCERPT_CHARS = 8000


def build_method_spec_prompt(analysis: PaperAnalysis, full_text: str = "") -> str:
    template = load_prompt(PROMPT_NAME)
    prompt = template.format(
        title=analysis.paper.title,
        abstract=analysis.paper.abstract,
        proposed_method=analysis.proposed_method,
        datasets=", ".join(analysis.datasets) or "not identified",
    )
    # Appended only when present, so the abstract-only prompt (and its
    # recorded fixtures) stays byte-identical.
    if full_text:
        prompt += "\n\nFull-text excerpts (authoritative over the abstract):\n"
        prompt += full_text[:FULLTEXT_EXCERPT_CHARS]
    return prompt


def field_match_rate(
    extracted: dict[str, Any],
    reference: dict[str, Any],
    fields: tuple[str, ...] = (
        "universe",
        "frequency",
        "signal_definition",
        "portfolio_construction",
        "rebalance_frequency",
        "holding_period",
    ),
) -> float:
    """Fraction of key fields that match the hand-labeled reference.

    String fields match on case-insensitive substring containment in either
    direction, so "monthly" matches "monthly, overlapping". This is the
    ground-truth check QB-19's acceptance uses against the labeled fixtures.
    """

    if not fields:
        return 0.0
    hits = 0
    for field_name in fields:
        got = str(extracted.get(field_name, "")).strip().lower()
        want = str(reference.get(field_name, "")).strip().lower()
        if want and got and (want in got or got in want):
            hits += 1
        elif not want and not got:
            hits += 1
    return hits / len(fields)


class MethodSpecExtractionSkill:
    """Extract a structured, schema-validated MethodSpec for the coder."""

    name = "method_spec_extraction"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis: PaperAnalysis = inputs["analysis"]
        full_text = str(inputs.get("full_text") or "")
        notes: list[str] = []
        spec_payload: dict[str, Any] | None = None
        source = "metadata_fallback"
        evidence: list[dict[str, str]] = []

        if ctx.llm is None:
            notes.append("no LLM configured; using deterministic metadata fallback")
        else:
            prompt = build_method_spec_prompt(analysis, full_text)
            try:
                response = ctx.llm.complete(prompt, system=SYSTEM_PROMPT)
                candidate = extract_json_object(response.text)
                errors = validate(candidate, METHOD_SPEC_SCHEMA)
                if errors:
                    notes.append(
                        "LLM output failed schema validation: "
                        + "; ".join(errors[:5])
                    )
                else:
                    spec_payload = _normalize(candidate)
                    if full_text:
                        # Full text is authoritative: floor the confidence so
                        # a full-text extraction outranks the metadata fallback.
                        source = "llm_fulltext"
                        spec_payload["confidence"] = max(
                            spec_payload["confidence"], FULLTEXT_CONFIDENCE_FLOOR
                        )
                        detail = "schema-validated full-text completion via the LLM seam"
                    else:
                        source = "llm"
                        detail = "schema-validated completion via the LLM seam"
                    evidence = [
                        {
                            "kind": "artifact",
                            "reference": f"llm:{response.fingerprint}",
                            "detail": detail,
                        }
                    ]
            except Exception as exc:  # boundary: fall back, but record why
                notes.append(f"LLM extraction failed: {exc!r}")

        if spec_payload is None:
            spec_payload = _metadata_method_spec(analysis)
            source = "metadata_fallback"
            evidence = [
                {
                    "kind": "paper_quote",
                    "reference": "abstract",
                    "detail": "deterministic metadata heuristics",
                }
            ]
            notes.append("deterministic metadata fallback produced the spec")

        spec_payload["evidence"] = evidence
        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={
                "method_spec": spec_payload,
                "confidence": spec_payload["confidence"],
                "source": source,
            },
            notes=tuple(notes),
        )
        ctx.manifest.record_skill(result)
        return result


def method_spec_from_payload(paper: Paper, payload: dict[str, Any]) -> MethodSpec | None:
    """Build the frozen MethodSpec from a skill payload (JSON-shaped)."""

    data = payload.get("method_spec")
    if not data:
        return None
    return MethodSpec(
        paper=paper,
        universe=str(data.get("universe", "")),
        frequency=str(data.get("frequency", "")),
        signal_definition=str(data.get("signal_definition", "")),
        portfolio_construction=str(data.get("portfolio_construction", "")),
        rebalance_frequency=str(data.get("rebalance_frequency", "")),
        holding_period=str(data.get("holding_period", "")),
        sample_start=_parse_date(data.get("sample_start")),
        sample_end=_parse_date(data.get("sample_end")),
        evaluation_protocol=str(data.get("evaluation_protocol", "")),
        hyperparameters=dict(data.get("hyperparameters") or {}),
        data_requirements=tuple(str(item) for item in data.get("data_requirements") or ()),
        extraction_confidence=float(data.get("confidence", 0.0)),
        evidence=tuple(
            EvidenceLink(
                kind=str(item.get("kind", "")),
                reference=str(item.get("reference", "")),
                detail=str(item.get("detail", "")),
            )
            for item in data.get("evidence") or ()
        ),
    )


def _normalize(candidate: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(candidate)
    normalized.setdefault("sample_start", None)
    normalized.setdefault("sample_end", None)
    normalized.setdefault("evaluation_protocol", "")
    normalized.setdefault("hyperparameters", {})
    normalized.setdefault("data_requirements", [])
    normalized["confidence"] = max(0.0, min(1.0, float(normalized["confidence"])))
    return normalized


def _metadata_method_spec(analysis: PaperAnalysis) -> dict[str, Any]:
    text = f"{analysis.paper.title}. {analysis.paper.abstract}"
    lowered = text.lower()

    if "daily" in lowered:
        frequency = "daily"
    elif "weekly" in lowered:
        frequency = "weekly"
    else:
        frequency = "monthly"

    universe_terms = [marker for marker in _UNIVERSE_MARKERS if marker in lowered]
    universe = (
        ", ".join(term.upper() if len(term) <= 6 else term for term in universe_terms)
        or "unspecified universe"
    )

    construction_terms = [m for m in _CONSTRUCTION_MARKERS if m in lowered]
    construction = ", ".join(construction_terms) or "unspecified construction"

    hyperparameters: dict[str, Any] = {}
    signal = analysis.proposed_method
    past_return = _PAST_RETURN.search(lowered)
    if past_return:
        months = int(past_return.group(1))
        signal = f"ranking on past {months}-month returns"
        hyperparameters["formation_months"] = months

    holding_period = "unspecified"
    holding = _HOLDING.search(lowered)
    if holding:
        months = int(holding.group(1))
        overlapping = bool(holding.group(2))
        holding_period = f"{months} months" + (", overlapping" if overlapping else "")
        hyperparameters["holding_months"] = months

    sample_start = sample_end = None
    period = _SAMPLE_PERIOD.search(text)
    if period:
        sample_start = f"{period.group(1)}-01-01"
        sample_end = f"{period.group(2)}-12-31"

    return {
        "universe": universe,
        "frequency": frequency,
        "signal_definition": signal,
        "portfolio_construction": construction,
        "rebalance_frequency": frequency,
        "holding_period": holding_period,
        "sample_start": sample_start,
        "sample_end": sample_end,
        "evaluation_protocol": "",
        "hyperparameters": hyperparameters,
        "data_requirements": list(analysis.datasets),
        "confidence": FALLBACK_CONFIDENCE,
    }


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


@register_skill("quant_reader", "method_spec_extraction")
def _make_method_spec_skill() -> MethodSpecExtractionSkill:
    return MethodSpecExtractionSkill()
