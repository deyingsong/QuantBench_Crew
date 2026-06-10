"""Target-table extraction: headline claims into a ReproductionTarget.

Without a quantitative target, reproduction is unfalsifiable — so this skill
either produces claims with values, tolerances, and sources, or reports
"skipped" loudly. The LLM path is schema-validated; the deterministic
fallback scans the abstract for explicit numeric claims (percent-per-period
and Sharpe-ratio phrasings) and never invents numbers.
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
_SHARPE = re.compile(r"sharpe ratios? of\s*(\d+(?:\.\d+)?)", re.IGNORECASE)


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
    claims: list[dict[str, Any]] = []
    for match in _PERCENT_PER_PERIOD.finditer(paper.abstract):
        period = match.group(2).lower()
        claims.append(
            {
                "metric": "monthly_return" if period == "month" else "annual_return",
                "value": float(match.group(1)) / 100.0,
                "unit": "monthly" if period == "month" else "annualized",
                "context": _surrounding_text(paper.abstract, match.start(), match.end()),
                "source": "abstract",
            }
        )
    for match in _SHARPE.finditer(paper.abstract):
        claims.append(
            {
                "metric": "sharpe",
                "value": float(match.group(1)),
                "unit": "annualized",
                "context": _surrounding_text(paper.abstract, match.start(), match.end()),
                "source": "abstract",
            }
        )
    return {"table_reference": "", "claims": claims, "notes": []}


def _surrounding_text(text: str, start: int, end: int, radius: int = 80) -> str:
    snippet = text[max(0, start - radius) : min(len(text), end + radius)]
    return " ".join(snippet.split())


@register_skill("quant_reader", "target_table_extraction")
def _make_target_table_skill() -> TargetTableExtractionSkill:
    return TargetTableExtractionSkill()
