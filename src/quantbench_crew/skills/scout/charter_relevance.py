"""Charter-relevance ranking: score candidates against a research charter.

A `ResearchCharter` states what the operator actually wants to study; this
skill scores each candidate's relevance to it and feeds that score into the
scout ranking, so an on-charter paper with few keyword hits can outrank a
keyword-dense but off-charter one. The default scorer is deterministic
charter-overlap (`method="charter_overlap"`); an embedding backend can be
injected later (`method="embedding"`) without changing the seam, with the
overlap path as the permanent offline fallback.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Protocol

from quantbench_crew.models import Paper, RelevanceAssessment, ResearchCharter
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings

DEFAULT_RELEVANCE_BOOST = 10.0


class EmbeddingBackend(Protocol):
    """Optional embedding seam; absent by default (overlap fallback used)."""

    def available(self) -> bool: ...

    def relevance(self, charter_text: str, paper_text: str) -> float: ...


def load_charter(config: Mapping[str, Any]) -> ResearchCharter | None:
    """Build a ResearchCharter from the scout config, if one is declared."""

    scout = (config.get("agents") or {}).get("quant_scout") or {}
    charter = scout.get("charter")
    if not charter:
        return None
    return ResearchCharter(
        purpose=str(charter.get("purpose", "")),
        themes=tuple(str(t) for t in charter.get("themes", ())),
        must_have=tuple(str(t) for t in charter.get("must_have", ())),
        exclude=tuple(str(t) for t in charter.get("exclude", ())),
        source_path=str(charter.get("source_path", "")),
    )


def assess_relevance(
    paper: Paper,
    charter: ResearchCharter,
    embedder: EmbeddingBackend | None = None,
) -> RelevanceAssessment:
    """Score one paper's charter relevance in [0, 1]."""

    paper_text = " ".join((paper.title, paper.abstract, " ".join(paper.keywords)))
    if embedder is not None and embedder.available():
        charter_text = " ".join(
            (charter.purpose, *charter.themes, *charter.must_have)
        )
        score = max(0.0, min(1.0, embedder.relevance(charter_text, paper_text)))
        return RelevanceAssessment(score=score, method="embedding")

    lowered = paper_text.lower()
    matched_themes = tuple(theme for theme in charter.themes if _present(theme, lowered))
    theme_overlap = (len(matched_themes) / len(charter.themes)) if charter.themes else 0.0
    must_hits = sum(1 for phrase in charter.must_have if _present(phrase, lowered))
    must_fraction = (must_hits / len(charter.must_have)) if charter.must_have else 1.0
    excluded = [phrase for phrase in charter.exclude if _present(phrase, lowered)]

    # Themes carry the signal; must-haves gate; any exclusion halves the score.
    score = 0.6 * theme_overlap + 0.4 * must_fraction
    if excluded:
        score *= 0.5
    score = max(0.0, min(1.0, score))

    rationale = (
        f"themes {len(matched_themes)}/{len(charter.themes)}, "
        f"must-have {must_hits}/{len(charter.must_have)}"
        + (f", excluded by {excluded}" if excluded else "")
    )
    return RelevanceAssessment(
        score=score,
        method="charter_overlap",
        matched_themes=matched_themes,
        rationale=rationale,
    )


class CharterRelevanceSkill:
    """Record a paper's charter-relevance assessment in the run manifest."""

    name = "charter_relevance"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        assessment: RelevanceAssessment = inputs["relevance"]
        paper: Paper = inputs["paper"]
        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={
                "score": assessment.score,
                "method": assessment.method,
                "matched_themes": list(assessment.matched_themes),
                "rationale": assessment.rationale,
                "title": paper.title,
            },
            notes=(f"charter relevance {assessment.score:.2f} ({assessment.method})",),
        )
        ctx.manifest.record_skill(result)
        return result


def relevance_boost(config: Mapping[str, Any]) -> float:
    settings = skill_settings(config, "quant_scout", "charter_relevance")
    return float(settings.get("relevance_boost", DEFAULT_RELEVANCE_BOOST))


def _present(phrase: str, lowered_text: str) -> bool:
    phrase = phrase.strip().lower()
    if not phrase:
        return False
    # Word-boundary match for single tokens; substring for multi-word phrases.
    if " " in phrase:
        return phrase in lowered_text
    return re.search(rf"\b{re.escape(phrase)}\b", lowered_text) is not None


@register_skill("quant_scout", "charter_relevance")
def _make_charter_relevance_skill() -> CharterRelevanceSkill:
    return CharterRelevanceSkill()
