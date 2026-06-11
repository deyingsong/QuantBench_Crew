"""Target-table extraction: falsifiable claims into a ReproductionTarget.

Without a quantitative target, reproduction is unfalsifiable — so this skill
either produces claims with values, tolerances, and sources, or reports
"skipped" loudly. The LLM path is schema-validated; the deterministic
fallback enumerates *every* explicit numeric claim it can recognize
(returns per period, Sharpe, t-statistics, alpha, information ratio) and
never invents numbers. Enumerating the full claim set — not just the headline
— is what lets the bench check a paper on more than one falsifiable axis.
"""

from __future__ import annotations

import re
from typing import Any

from quantbench_crew.models import Claim, Paper, ReproductionTarget
from quantbench_crew.prompts import load_prompt
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.skills.validation import extract_json_object, validate

PROMPT_NAME = "target_table_extraction"
SYSTEM_PROMPT = (
    "You identify the headline quantitative results of finance papers as "
    "reproduction targets. Answer with a single JSON object only."
)
DEFAULT_TOLERANCE = 0.2

TARGET_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["claims"],
    "properties": {
        "table_reference": {"type": "string"},
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["metric", "value"],
                "properties": {
                    "metric": {"type": "string"},
                    "value": {"type": "number"},
                    "unit": {"type": "string"},
                    "context": {"type": "string"},
                    "tolerance": {"type": "number"},
                    "source": {"type": "string"},
                },
            },
        },
        "notes": {"type": "array", "items": {"type": "string"}},
    },
}

_PERCENT_PER_PERIOD = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*per\s*(month|year|annum)", re.IGNORECASE
)
_SHARPE = re.compile(
    r"(?:annualized\s+)?sharpe(?:\s+ratio)?s?\s+of\s+(\d+(?:\.\d+)?)", re.IGNORECASE
)
_TSTAT = re.compile(
    r"t-?stat(?:istic)?s?\s*(?:of|=|:)\s*(\d+(?:\.\d+)?)", re.IGNORECASE
)
_ALPHA = re.compile(
    r"(monthly|annual|annualized)?\s*alpha\s+of\s+(\d+(?:\.\d+)?)\s*(?:%|percent)"
    r"(?:\s*per\s*(month|year))?",
    re.IGNORECASE,
)
_INFO_RATIO = re.compile(
    r"information ratios?\s+of\s+(\d+(?:\.\d+)?)", re.IGNORECASE
)


def build_target_table_prompt(paper: Paper) -> str:
    template = load_prompt(PROMPT_NAME)
    return template.format(title=paper.title, abstract=paper.abstract)


class TargetTableExtractionSkill:
    """Extract reproduction-target claims from the paper's headline results."""

    name = "target_table_extraction"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis = inputs["analysis"]
        paper: Paper = analysis.paper
        settings = skill_settings(ctx.config, "quant_reader", self.name)
        default_tolerance = float(settings.get("default_tolerance", DEFAULT_TOLERANCE))

        notes: list[str] = []
        target_payload: dict[str, Any] | None = None
        source = "abstract_fallback"

        if ctx.llm is None:
            notes.append("no LLM configured; using deterministic abstract fallback")
        else:
            prompt = build_target_table_prompt(paper)
            try:
                response = ctx.llm.complete(prompt, system=SYSTEM_PROMPT)
                candidate = extract_json_object(response.text)
                errors = validate(candidate, TARGET_SCHEMA)
                if errors:
                    notes.append(
                        "LLM output failed schema validation: "
                        + "; ".join(errors[:5])
                    )
                else:
                    target_payload = candidate
                    source = "llm"
            except Exception as exc:  # boundary: fall back, but record why
                notes.append(f"LLM extraction failed: {exc!r}")

        if target_payload is None:
            target_payload = _abstract_claims(paper)
            source = "abstract_fallback"
            notes.append("deterministic abstract scan produced the claims")

        claims = [
            _normalize_claim(claim, default_tolerance)
            for claim in target_payload.get("claims", [])
        ]
        target_payload = {
            "table_reference": str(target_payload.get("table_reference", "")),
            "claims": claims,
            "notes": [str(note) for note in target_payload.get("notes", [])],
        }

        if not claims:
            result = SkillResult(
                skill=self.name,
                status="skipped",
                payload={"target": target_payload, "source": source},
                notes=(
                    *notes,
                    "no quantitative claims found; reproduction target is "
                    "unfalsifiable for this paper",
                ),
            )
        else:
            result = SkillResult(
                skill=self.name,
                status="ok",
                payload={"target": target_payload, "source": source},
                notes=tuple(notes),
            )
        ctx.manifest.record_skill(result)
        return result


def reproduction_target_from_payload(
    paper: Paper, payload: dict[str, Any]
) -> ReproductionTarget | None:
    """Build the frozen ReproductionTarget from a skill payload."""

    data = payload.get("target") or {}
    claims = tuple(
        Claim(
            metric=str(item["metric"]),
            value=float(item["value"]),
            unit=str(item.get("unit", "")),
            context=str(item.get("context", "")),
            tolerance=float(item.get("tolerance", DEFAULT_TOLERANCE)),
            source=str(item.get("source", "")),
        )
        for item in data.get("claims", [])
        if item.get("metric") and item.get("value") is not None
    )
    if not claims:
        return None
    return ReproductionTarget(
        paper=paper,
        claims=claims,
        table_reference=str(data.get("table_reference", "")),
        notes=tuple(str(note) for note in data.get("notes", [])),
    )


def _normalize_claim(claim: dict[str, Any], default_tolerance: float) -> dict[str, Any]:
    return {
        "metric": str(claim.get("metric", "")),
        "value": float(claim.get("value", 0.0)),
        "unit": str(claim.get("unit", "")),
        "context": str(claim.get("context", "")),
        "tolerance": float(claim.get("tolerance", default_tolerance)),
        "source": str(claim.get("source", "")) or "abstract",
    }


def _abstract_claims(paper: Paper) -> dict[str, Any]:
    text = paper.abstract
    claims: list[dict[str, Any]] = []

    def add(metric: str, value: float, unit: str, start: int, end: int) -> None:
        claims.append(
            {
                "metric": metric,
                "value": value,
                "unit": unit,
                "context": _surrounding_text(text, start, end),
                "source": "abstract",
            }
        )

    for m in _PERCENT_PER_PERIOD.finditer(text):
        period = m.group(2).lower()
        add(
            "monthly_return" if period == "month" else "annual_return",
            float(m.group(1)) / 100.0,
            "monthly" if period == "month" else "annualized",
            m.start(), m.end(),
        )
    for m in _SHARPE.finditer(text):
        add("sharpe", float(m.group(1)), "annualized", m.start(), m.end())
    for m in _TSTAT.finditer(text):
        add("t_statistic", float(m.group(1)), "", m.start(), m.end())
    for m in _ALPHA.finditer(text):
        period = (m.group(3) or "").lower()
        unit = "monthly" if period == "month" else "annualized" if period == "year" else (m.group(1) or "").lower()
        add("alpha", float(m.group(2)) / 100.0, unit or "monthly", m.start(), m.end())
    for m in _INFO_RATIO.finditer(text):
        add("information_ratio", float(m.group(1)), "annualized", m.start(), m.end())

    return {"table_reference": "", "claims": _dedup_claims(claims), "notes": []}


def _dedup_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, float]] = set()
    unique: list[dict[str, Any]] = []
    for claim in claims:
        key = (claim["metric"], round(claim["value"], 6))
        if key not in seen:
            seen.add(key)
            unique.append(claim)
    return unique


def _surrounding_text(text: str, start: int, end: int, radius: int = 80) -> str:
    snippet = text[max(0, start - radius) : min(len(text), end + radius)]
    return " ".join(snippet.split())


@register_skill("quant_reader", "target_table_extraction")
def _make_target_table_skill() -> TargetTableExtractionSkill:
    return TargetTableExtractionSkill()
