"""Research-value scoring for Scout-stage paper prioritization."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from quantbench_crew.models import Paper, RelevanceAssessment, ResearchCharter
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings
from quantbench_crew.skills.scout.charter_relevance import assess_relevance
from quantbench_crew.skills.scout.triage import (
    CODE_MARKERS,
    PROPRIETARY_MARKERS,
    PUBLIC_MARKERS,
    VENDOR_MARKERS,
)

DEFAULT_RELEVANCE_BOOST = 10.0

DIMENSION_WEIGHTS = {
    "charter_fit": 0.35,
    "empirical_evidence": 0.20,
    "implementability": 0.20,
    "economic_relevance": 0.15,
    "information_gain": 0.10,
}

EVIDENCE_SIGNALS = {
    "out-of-sample evidence": ("out-of-sample", "out of sample", "walk-forward", "walk forward"),
    "robustness checks": ("robustness", "sensitivity analysis", "subsample", "placebo"),
    "baseline comparison": ("baseline", "benchmark", "compared with", "relative to"),
    "falsifiable quantitative claim": (),
}
IMPLEMENTABILITY_SIGNALS = {
    "released code": (*CODE_MARKERS, "released code", "code release"),
    "named public data": (*PUBLIC_MARKERS, "public data"),
    "named vendor data": VENDOR_MARKERS,
    "implementation detail": (
        "portfolio construction",
        "rebalance",
        "holding period",
        "hyperparameter",
        "algorithm",
    ),
}
ECONOMIC_SIGNALS = {
    "net of costs": ("net of costs", "after transaction costs", "transaction costs", "trading costs"),
    "turnover disclosed": ("turnover",),
    "capacity or liquidity": ("capacity", "liquidity", "market impact", "slippage"),
    "risk disclosed": ("drawdown", "tail risk", "risk-adjusted", "sharpe ratio"),
    "economic mechanism": ("mechanism", "economic rationale", "why it works"),
}
INFORMATION_SIGNALS = {
    "new data or setting": ("new dataset", "novel dataset", "new market", "previously undocumented"),
    "new method": ("novel method", "new method", "we introduce", "we propose"),
    "challenges prior evidence": ("contrary to", "fails to replicate", "revisit", "re-examine"),
}

_NUMERIC_CLAIM = re.compile(r"\d+(?:\.\d+)?\s*(?:%|percent|bps|basis points)|sharpe", re.I)


def assess_research_value(
    paper: Paper,
    charter: ResearchCharter | None = None,
    weights: Mapping[str, float] | None = None,
) -> RelevanceAssessment:
    """Estimate research value from disclosed metadata without inventing evidence."""

    text = " ".join((paper.title, paper.abstract, " ".join(paper.keywords))).lower()
    active_weights = dict(weights or DIMENSION_WEIGHTS)

    charter_assessment = assess_relevance(paper, charter) if charter else None
    charter_fit = charter_assessment.score if charter_assessment else 0.5
    matched_themes = charter_assessment.matched_themes if charter_assessment else ()

    signals: list[str] = []
    evidence = _signal_score(text, EVIDENCE_SIGNALS, signals, base=0.10, step=0.22)
    if _NUMERIC_CLAIM.search(text):
        signals.append("falsifiable quantitative claim")
        evidence = min(1.0, evidence + 0.18)

    implementability = _signal_score(
        text, IMPLEMENTABILITY_SIGNALS, signals, base=0.10, step=0.22
    )
    economic = _signal_score(text, ECONOMIC_SIGNALS, signals, base=0.05, step=0.18)
    information = _signal_score(text, INFORMATION_SIGNALS, signals, base=0.15, step=0.25)

    dimensions = {
        "charter_fit": charter_fit,
        "empirical_evidence": evidence,
        "implementability": implementability,
        "economic_relevance": economic,
        "information_gain": information,
    }
    penalties: list[str] = []
    penalty = 0.0
    is_strategy = any(marker in text for marker in ("trading strategy", "portfolio", "alpha", "returns"))
    if is_strategy and not any(marker in text for marker in ECONOMIC_SIGNALS["net of costs"]):
        penalties.append("strategy economics omit transaction costs")
        penalty += 0.06
    if any(marker in text for marker in PROPRIETARY_MARKERS):
        penalties.append("proprietary data limits reproducibility")
        penalty += 0.08
    if "in-sample" in text and not any(
        marker in text for marker in EVIDENCE_SIGNALS["out-of-sample evidence"]
    ):
        penalties.append("in-sample evidence without disclosed out-of-sample test")
        penalty += 0.10
    if len(paper.abstract.split()) < 25 and len(signals) < 2:
        penalties.append("insufficient abstract detail")
        penalty += 0.05

    weighted = sum(active_weights[name] * dimensions[name] for name in active_weights)
    score = max(0.0, min(1.0, weighted - penalty))
    confidence = min(
        1.0,
        0.2
        + min(len(paper.abstract.split()), 200) / 400
        + (0.15 if paper.authors else 0.0)
        + (0.15 if paper.url else 0.0)
        + (0.10 if paper.published else 0.0),
    )
    rationale = (
        ", ".join(f"{name}={value:.2f}" for name, value in dimensions.items())
        + (f"; penalties: {', '.join(penalties)}" if penalties else "")
    )
    return RelevanceAssessment(
        score=score,
        method="research_value_rubric",
        matched_themes=matched_themes,
        rationale=rationale,
        dimensions=dimensions,
        signals=tuple(dict.fromkeys(signals)),
        penalties=tuple(penalties),
        confidence=confidence,
    )


class RelevanceScorerSkill:
    """Record a multi-dimensional Scout relevance assessment."""

    name = "relevance_scorer"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        assessment: RelevanceAssessment = inputs["relevance"]
        paper: Paper = inputs["paper"]
        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={
                "title": paper.title,
                "score": assessment.score,
                "method": assessment.method,
                "dimensions": assessment.dimensions,
                "signals": list(assessment.signals),
                "penalties": list(assessment.penalties),
                "confidence": assessment.confidence,
                "rationale": assessment.rationale,
            },
            notes=(f"research-value relevance {assessment.score:.2f}",),
        )
        ctx.manifest.record_skill(result)
        return result


def relevance_boost(config: Mapping[str, Any]) -> float:
    settings = skill_settings(config, "quant_scout", "relevance_scorer")
    return float(settings.get("relevance_boost", DEFAULT_RELEVANCE_BOOST))


def _signal_score(
    text: str,
    groups: Mapping[str, tuple[str, ...]],
    signals: list[str],
    *,
    base: float,
    step: float,
) -> float:
    hits = 0
    for label, markers in groups.items():
        if markers and any(marker in text for marker in markers):
            hits += 1
            signals.append(label)
    return min(1.0, base + hits * step)


@register_skill("quant_scout", "relevance_scorer")
def _make_relevance_scorer_skill() -> RelevanceScorerSkill:
    return RelevanceScorerSkill()
