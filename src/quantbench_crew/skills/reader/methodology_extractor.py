"""Extract scientific methodology, equations, algorithms, and settings."""

from __future__ import annotations

from typing import Any

from quantbench_crew.models import MethodologyAssessment, Paper, PaperAnalysis
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult
from quantbench_crew.skills.reader.structured_components import (
    EVIDENCE_SCHEMA,
    evidence_items,
    evidence_links,
    run_component_extraction,
    sentences_matching,
    source_text,
    string_tuple,
)

PROMPT_NAME = "methodology_extractor"
SYSTEM_PROMPT = (
    "You reconstruct scientific methods from research papers. Preserve "
    "equations and omissions, and answer with one JSON object."
)
METHODOLOGY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "summary",
        "equations",
        "algorithms",
        "experiment_settings",
        "baselines",
        "omitted_details",
        "confidence",
        "evidence",
    ],
    "properties": {
        "summary": {"type": "string"},
        "equations": {"type": "array", "items": {"type": "string"}},
        "algorithms": {"type": "array", "items": {"type": "string"}},
        "experiment_settings": {"type": "array", "items": {"type": "string"}},
        "baselines": {"type": "array", "items": {"type": "string"}},
        "omitted_details": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
        "evidence": EVIDENCE_SCHEMA,
    },
}


class MethodologyExtractorSkill:
    """Extract how a paper scientifically answers its question."""

    name = "methodology_extractor"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        return run_component_extraction(
            ctx,
            analysis=inputs["analysis"],
            full_text=str(inputs.get("full_text") or ""),
            skill_name=self.name,
            payload_key="methodology_assessment",
            prompt_name=PROMPT_NAME,
            system_prompt=SYSTEM_PROMPT,
            schema=METHODOLOGY_SCHEMA,
            fallback=_fallback,
        )


def methodology_assessment_from_payload(
    paper: Paper, payload: dict[str, Any]
) -> MethodologyAssessment | None:
    """Build a typed methodology assessment from the skill payload."""

    data = payload.get("methodology_assessment")
    if not data:
        return None
    return MethodologyAssessment(
        summary=str(data.get("summary", "")),
        equations=string_tuple(data.get("equations")),
        algorithms=string_tuple(data.get("algorithms")),
        experiment_settings=string_tuple(data.get("experiment_settings")),
        baselines=string_tuple(data.get("baselines")),
        omitted_details=string_tuple(data.get("omitted_details")),
        confidence=float(data.get("confidence", 0.0)),
        evidence=evidence_links(data.get("evidence", [])),
    )


def _fallback(analysis: PaperAnalysis, full_text: str) -> dict[str, Any]:
    text = source_text(analysis, full_text)
    equations = sentences_matching(text, ("=", "equation", "objective function", "constraint"))
    algorithms = sentences_matching(
        text,
        (
            "algorithm",
            "regression",
            "neural network",
            "machine learning",
            "optimization",
            "estimate",
            "portfolio",
        ),
    )
    settings = sentences_matching(
        text,
        (
            "daily",
            "weekly",
            "monthly",
            "parameter",
            "horizon",
            "seed",
            "window",
            "experiment",
        ),
    )
    baselines = sentences_matching(text, ("baseline", "benchmark", "compared with", "versus"))
    evidence = []
    for field, values in (
        ("equations", equations),
        ("algorithms", algorithms),
        ("experiment_settings", settings),
        ("baselines", baselines),
    ):
        evidence.extend(evidence_items(field, values))
    if analysis.proposed_method in text:
        evidence.extend(evidence_items("summary", [analysis.proposed_method]))
    return {
        "summary": analysis.proposed_method,
        "equations": equations,
        "algorithms": algorithms,
        "experiment_settings": settings,
        "baselines": baselines,
        "omitted_details": [],
        "confidence": 0.35 if full_text else 0.2,
        "evidence": evidence,
    }


@register_skill("quant_reader", "methodology_extractor")
def _make_methodology_extractor_skill() -> MethodologyExtractorSkill:
    return MethodologyExtractorSkill()
