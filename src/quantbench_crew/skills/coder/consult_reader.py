"""Consult-Reader: close MethodSpec gaps by asking the Reader, not guessing.

The Coder's real input is the ``MethodSpec`` the Reader extracted. When a
performance-affecting field is missing, vague, or low-confidence, implementing a
guess silently biases the artifact the Bench then scores. This skill detects
those gaps deterministically, forms one hypothesis-carrying question per gap,
and — when resolution is enabled and a Reader backbone is available — routes the
questions to the Reader (``quant_reader``) for source-grounded answers. It is
the in-pipeline wiring behind the open-format ``consult-reader`` skill.

Offline-safe: with no Reader backbone, or with resolution disabled, the skill
still emits the gaps, questions, and hypotheses as an artifact so a harness
re-invocation or a human can resolve them. It never fabricates an answer. Where
a field stays unresolved (or the Reader replies "unspecified in source"), the
skill adopts a declared neutral default and records it as an explicit
assumption — never the value that would flatter the candidate's score.

Spend is bounded by the shared per-paper cost cap; a single resolution call is
made only when gaps exist, resolution is enabled, and a backbone is present.
"""

from __future__ import annotations

import json
from typing import Any

from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.llm import llm_for_agent
from quantbench_crew.models import MethodSpec, PaperAnalysis
from quantbench_crew.prompts import load_prompt
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.skills.validation import extract_json_object

PROMPT_NAME = "consult_reader"
SYSTEM_PROMPT = (
    "You are the Reader agent answering the Coder's clarification questions "
    "about a paper you have read. Answer only from the paper; say 'unspecified "
    "in source' when the paper does not state it. Output only a JSON object."
)
DEFAULT_CONFIDENCE_THRESHOLD = 0.5
DEFAULT_COST_CAP_USD = 2.0
ARTIFACT_PATH = "generated/reader_consultation.json"
UNSPECIFIED = "unspecified in source"

# Case-insensitive markers that make a non-empty field count as a gap.
VAGUE_MARKERS = (
    "not identified",
    "requires human review",
    "unclear",
    "n/a",
    "unspecified",
    "tbd",
    "metadata-only",
    "not stated",
)

# Required, performance-affecting fields with a neutral declared default and the
# question put to the Reader. The default is never the score-maximizing value.
_FIELD_DEFAULTS: dict[str, str] = {
    "universe": "US common stocks, price > $5",
    "frequency": "monthly",
    "signal_definition": "",  # filled from analysis.proposed_method at runtime
    "portfolio_construction": "decile long-short, equal-weight legs",
    "rebalance_frequency": "monthly",
    "holding_period": "1 month, non-overlapping",
}
_FIELD_QUESTIONS: dict[str, str] = {
    "universe": "What is the exact eligibility universe and its point-in-time filters?",
    "frequency": "At what bar frequency are signals and returns computed?",
    "signal_definition": "State the signal formula precisely, including window lengths and any skip period.",
    "portfolio_construction": "Long-only or long-short, and how are weights set and legs sized?",
    "rebalance_frequency": "How often are positions updated?",
    "holding_period": "How long are positions held, and are they overlapping?",
}
_REQUIRED_FIELDS = tuple(_FIELD_DEFAULTS)


def _is_vague(value: str) -> bool:
    text = (value or "").strip()
    if not text:
        return True
    lowered = text.lower()
    return any(marker in lowered for marker in VAGUE_MARKERS)


def _default_for(field: str, analysis: PaperAnalysis) -> str:
    if field == "signal_definition":
        return (analysis.proposed_method or "").strip() or "the paper's proposed signal"
    return _FIELD_DEFAULTS[field]


def detect_gaps(analysis: PaperAnalysis, confidence_threshold: float) -> list[dict[str, str]]:
    """Return performance-affecting spec gaps, each with a hypothesis default.

    Pure and deterministic: no LLM. With no MethodSpec, every required field is
    a gap; otherwise empty/vague fields and an overall low-confidence flag are.
    """

    spec: MethodSpec | None = analysis.method_spec
    gaps: list[dict[str, str]] = []

    if spec is None:
        for field in _REQUIRED_FIELDS:
            gaps.append(
                {
                    "field": field,
                    "issue": "no MethodSpec extracted",
                    "hypothesis": _default_for(field, analysis),
                    "question": _FIELD_QUESTIONS[field],
                }
            )
        return gaps

    for field in _REQUIRED_FIELDS:
        value = str(getattr(spec, field, "") or "")
        if _is_vague(value):
            gaps.append(
                {
                    "field": field,
                    "issue": "empty or vague in MethodSpec",
                    "hypothesis": _default_for(field, analysis),
                    "question": _FIELD_QUESTIONS[field],
                }
            )

    if float(getattr(spec, "extraction_confidence", 0.0)) < confidence_threshold:
        gaps.append(
            {
                "field": "overall",
                "issue": f"extraction_confidence below {confidence_threshold:g}",
                "hypothesis": "the extracted spec is faithful to the paper",
                "question": "Confirm the extracted universe, signal, and construction are faithful to the paper.",
            }
        )

    return gaps


def build_consult_prompt(analysis: PaperAnalysis, gaps: list[dict[str, str]]) -> str:
    """Render the Reader-directed consultation prompt for the given gaps."""

    template = load_prompt(PROMPT_NAME)
    questions_block = "\n".join(
        f"- {gap['field']}: {gap['question']} (Coder's guess: {gap['hypothesis']})"
        for gap in gaps
    )
    return template.format(
        paper_title=analysis.paper.title,
        abstract=(analysis.paper.abstract or "").strip() or "not available",
        proposed_method=(analysis.proposed_method or "").strip() or "not available",
        datasets=", ".join(analysis.datasets) or "not available",
        metrics=", ".join(analysis.metrics) or "not available",
        questions_block=questions_block,
    )


class ConsultReaderSkill:
    """Detect spec gaps and (optionally) resolve them with the Reader backbone."""

    name = "consult_reader"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis: PaperAnalysis = inputs["analysis"]
        settings = skill_settings(ctx.config, "quant_coder", self.name)
        threshold = float(settings.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD))
        resolve = bool(settings.get("resolve", False))
        llm_config = ctx.config.get("llm") or {}
        cost_cap = float(llm_config.get("cost_cap_usd", DEFAULT_COST_CAP_USD))

        gaps = detect_gaps(analysis, threshold)
        notes: list[str] = []

        if not gaps:
            result = SkillResult(
                skill=self.name,
                status="skipped",
                payload={"gaps": [], "questions": [], "answers": {}, "assumptions": [],
                         "resolved": False, "consulted": "none"},
                notes=("MethodSpec complete on performance-affecting fields; no consultation needed",),
            )
            ctx.manifest.record_skill(result)
            return result

        questions = [f"{gap['field']}: {gap['question']}" for gap in gaps]
        answers: dict[str, str] = {}
        consulted = "none"

        if resolve:
            reader = llm_for_agent(ctx.llm, "quant_reader")
            if reader is None:
                notes.append(
                    "resolution enabled but no Reader backbone available; "
                    "emitting questions for harness/human routing"
                )
            else:
                spent = sum(float(call.get("cost_usd", 0.0)) for call in ctx.manifest.llm_calls)
                if spent >= cost_cap:
                    notes.append(
                        f"per-paper cost cap reached (${spent:.4f} >= ${cost_cap:.2f}); "
                        "skipping Reader consultation"
                    )
                else:
                    try:
                        response = reader.complete(
                            build_consult_prompt(analysis, gaps), system=SYSTEM_PROMPT
                        )
                        parsed = extract_json_object(response.text) or {}
                        answers = {
                            str(k): str(v).strip()
                            for k, v in parsed.items()
                            if str(v).strip()
                        }
                        consulted = "quant_reader"
                        notes.append(f"consulted Reader; {len(answers)} field(s) answered")
                    except Exception as exc:  # boundary: record and emit questions
                        notes.append(f"Reader consultation failed: {exc!r}")
        else:
            notes.append("resolution disabled; emitting questions only")

        # Adopt declared neutral defaults where the Reader did not resolve a
        # field (or replied "unspecified in source"); record each as an
        # explicit assumption so the Bench and Reviewer can stress it.
        assumptions: list[str] = []
        for gap in gaps:
            field = gap["field"]
            if field == "overall":
                continue
            answer = answers.get(field, "")
            if not answer or UNSPECIFIED in answer.lower():
                assumptions.append(f"{field}: assuming '{gap['hypothesis']}' ({UNSPECIFIED})")

        payload: dict[str, Any] = {
            "gaps": gaps,
            "questions": questions,
            "answers": answers,
            "assumptions": assumptions,
            "resolved": bool(answers),
            "consulted": consulted,
        }
        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        store.write_json(ARTIFACT_PATH, payload)

        result = SkillResult(
            skill=self.name,
            status="ok",
            payload=payload,
            artifacts=(ARTIFACT_PATH,),
            notes=tuple(notes),
        )
        ctx.manifest.record_skill(result)
        return result


@register_skill("quant_coder", "consult_reader")
def _make_consult_reader_skill() -> ConsultReaderSkill:
    return ConsultReaderSkill()
