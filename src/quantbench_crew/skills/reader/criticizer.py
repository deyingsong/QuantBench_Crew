"""Identify assumptions, limitations, validity threats, and future work."""

from __future__ import annotations

from typing import Any

from quantbench_crew.models import CritiqueAssessment, Paper, PaperAnalysis
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
    substantive_strings,
)

PROMPT_NAME = "criticizer"
SYSTEM_PROMPT = (
    "You critically evaluate research papers without inventing flaws. "
    "Separate author-stated limits from your inferred validity threats and answer with one JSON object."
)
CRITIQUE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "assumptions",
        "author_stated_limitations",
        "reader_inferred_threats",
        "unanswered_questions",
        "future_directions",
        "confidence",
        "evidence",
    ],
    "properties": {
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "author_stated_limitations": {"type": "array", "items": {"type": "string"}},
        "reader_inferred_threats": {"type": "array", "items": {"type": "string"}},
        "unanswered_questions": {"type": "array", "items": {"type": "string"}},
        "future_directions": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
        "evidence": EVIDENCE_SCHEMA,
    },
}


class CriticizerSkill:
    """Extract grounded assumptions, limitations, and future directions."""

    name = "criticizer"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        return run_component_extraction(
            ctx,
            analysis=inputs["analysis"],
            full_text=str(inputs.get("full_text") or ""),
            skill_name=self.name,
            payload_key="critique",
            prompt_name=PROMPT_NAME,
            system_prompt=SYSTEM_PROMPT,
            schema=CRITIQUE_SCHEMA,
            fallback=_fallback,
        )


def critique_from_payload(paper: Paper, payload: dict[str, Any]) -> CritiqueAssessment | None:
    """Build a typed critique assessment from the skill payload."""

    data = payload.get("critique")
    if not data:
        return None
    return CritiqueAssessment(
        assumptions=string_tuple(data.get("assumptions")),
        author_stated_limitations=string_tuple(data.get("author_stated_limitations")),
        reader_inferred_threats=string_tuple(data.get("reader_inferred_threats")),
        unanswered_questions=string_tuple(data.get("unanswered_questions")),
        future_directions=string_tuple(data.get("future_directions")),
        confidence=float(data.get("confidence", 0.0)),
        evidence=evidence_links(data.get("evidence", [])),
    )


def _fallback(analysis: PaperAnalysis, full_text: str) -> dict[str, Any]:
    text = source_text(analysis, full_text)
    assumptions = substantive_strings(analysis.assumptions)
    limitations = substantive_strings(analysis.limitations)
    stated_limitations = sentences_matching(
        text,
        (
            "limitation",
            "limited",
            "bias",
            "caveat",
            "may not",
            "cannot",
            "confound",
            "leakage",
            "not robust",
        ),
    )
    stated_limitations = list(dict.fromkeys([*limitations, *stated_limitations]))
    future = sentences_matching(
        text, ("future research", "future work", "further research", "could extend")
    )
    evidence = []
    evidence.extend(
        evidence_items(
            "assumptions", [item for item in assumptions if item in text]
        )
    )
    evidence.extend(evidence_items("author_stated_limitations", stated_limitations))
    evidence.extend(evidence_items("future_directions", future))
    return {
        "assumptions": assumptions,
        "author_stated_limitations": stated_limitations,
        "reader_inferred_threats": [],
        "unanswered_questions": [],
        "future_directions": future,
        "confidence": 0.35 if full_text else 0.2,
        "evidence": evidence,
    }


@register_skill("quant_reader", "criticizer")
def _make_criticizer_skill() -> CriticizerSkill:
    return CriticizerSkill()
