"""Extract the question, field context, importance, and research gap."""

from __future__ import annotations

from typing import Any

from quantbench_crew.models import Paper, PaperAnalysis, ResearchQuestionAssessment
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

PROMPT_NAME = "question_identifier"
SYSTEM_PROMPT = (
    "You identify a research paper's central question and scholarly gap. "
    "Use only supplied paper text and answer with one JSON object."
)
QUESTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "question",
        "field_state",
        "importance",
        "existing_method_gap",
        "claimed_contribution",
        "confidence",
        "evidence",
    ],
    "properties": {
        "question": {"type": "string"},
        "field_state": {"type": "array", "items": {"type": "string"}},
        "importance": {"type": "array", "items": {"type": "string"}},
        "existing_method_gap": {"type": "array", "items": {"type": "string"}},
        "claimed_contribution": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
        "evidence": EVIDENCE_SCHEMA,
    },
}


class QuestionIdentifierSkill:
    """Extract the paper's motivating research context."""

    name = "question_identifier"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        return run_component_extraction(
            ctx,
            analysis=inputs["analysis"],
            full_text=str(inputs.get("full_text") or ""),
            skill_name=self.name,
            payload_key="question_assessment",
            prompt_name=PROMPT_NAME,
            system_prompt=SYSTEM_PROMPT,
            schema=QUESTION_SCHEMA,
            fallback=_fallback,
        )


def question_assessment_from_payload(
    paper: Paper, payload: dict[str, Any]
) -> ResearchQuestionAssessment | None:
    """Build a typed assessment from the skill payload."""

    data = payload.get("question_assessment")
    if not data:
        return None
    return ResearchQuestionAssessment(
        question=str(data.get("question", "")),
        field_state=string_tuple(data.get("field_state")),
        importance=string_tuple(data.get("importance")),
        existing_method_gap=string_tuple(data.get("existing_method_gap")),
        claimed_contribution=string_tuple(data.get("claimed_contribution")),
        confidence=float(data.get("confidence", 0.0)),
        evidence=evidence_links(data.get("evidence", [])),
    )


def _fallback(analysis: PaperAnalysis, full_text: str) -> dict[str, Any]:
    text = source_text(analysis, full_text)
    field_state = sentences_matching(
        text, ("existing", "previous", "prior", "literature", "studies", "research")
    )
    importance = sentences_matching(
        text, ("important", "because", "challenge", "problem", "need", "impact")
    )
    gap = sentences_matching(
        text, ("however", "but", "gap", "limited", "fail", "lack", "remains", "unclear")
    )
    contribution = sentences_matching(
        text, ("we propose", "we introduce", "we develop", "we show", "we find")
    )
    evidence = []
    for field, values in (
        ("field_state", field_state),
        ("importance", importance),
        ("existing_method_gap", gap),
        ("claimed_contribution", contribution),
    ):
        evidence.extend(evidence_items(field, values))
    if analysis.research_question in text:
        evidence.extend(evidence_items("question", [analysis.research_question]))
    return {
        "question": analysis.research_question,
        "field_state": field_state,
        "importance": importance,
        "existing_method_gap": gap,
        "claimed_contribution": contribution,
        "confidence": 0.35 if full_text else 0.2,
        "evidence": evidence,
    }


@register_skill("quant_reader", "question_identifier")
def _make_question_identifier_skill() -> QuestionIdentifierSkill:
    return QuestionIdentifierSkill()
