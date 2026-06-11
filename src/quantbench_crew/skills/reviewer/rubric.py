"""Rubric verdict: evidence-linked scores and an honest verdict.

Every rubric dimension is scored from upstream evidence recorded in the run
manifest (triage feasibility, walk-forward metrics, claim comparisons, code
generation tests) and carries the :class:`EvidenceLink` that supports it —
the same report-only-what-you-can-cite discipline a good code review follows.

The verdict is deliberately conservative: if placeholder data was used
anywhere in the run, the verdict is ``scaffold-only`` regardless of how good
the placeholder numbers look. A confident "promising" backed by fake returns
is worse than nothing.
"""

from __future__ import annotations

from typing import Any

from quantbench_crew.models import (
    BenchmarkResult,
    EvidenceLink,
    PaperAnalysis,
    RubricScore,
)
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult

DIMENSIONS = (
    "reproducibility",
    "robustness",
    "net_of_cost_viability",
    "novelty_vs_baselines",
    "data_accessibility",
)

VERDICT_SCAFFOLD = "scaffold-only"


class RubricVerdictSkill:
    """Score the rubric from evidence and derive a defensible verdict."""

    name = "rubric_verdict"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        analysis: PaperAnalysis = inputs["analysis"]
        benchmark: BenchmarkResult = inputs["benchmark_result"]

        triage = _manifest_payload(ctx, "reproducibility_triage")
        walk_forward = _manifest_payload(ctx, "walk_forward")

        placeholder_used = walk_forward is None or any(
            "placeholder" in note.lower() for note in benchmark.notes
        )

        rubric = (
            _reproducibility(benchmark),
            _robustness(walk_forward),
            _net_of_cost_viability(benchmark, walk_forward),
            _novelty_vs_baselines(benchmark, walk_forward),
            _data_accessibility(triage),
        )

        verdict = _derive_verdict(rubric, walk_forward, placeholder_used)
        strengths = tuple(
            f"{score.dimension}: {score.rationale}"
            for score in rubric
            if score.score >= 3
        ) or ("No dimension scored strongly enough to call a strength.",)
        weaknesses = tuple(
            f"{score.dimension}: {score.rationale}"
            for score in rubric
            if score.score <= 1
        ) or ("No dimension scored a clear weakness.",)

        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={
                "verdict": verdict,
                "placeholder_used": placeholder_used,
                "rubric": [_rubric_dict(score) for score in rubric],
                "strengths": list(strengths),
                "weaknesses": list(weaknesses),
            },
            notes=(
                f"verdict {verdict!r}"
                + (" (placeholder data present)" if placeholder_used else ""),
            ),
        )
        ctx.manifest.record_skill(result)
        return result


def build_rubric(payload: dict[str, Any]) -> tuple[RubricScore, ...]:
    """Reconstruct typed RubricScore tuple from a skill payload."""

    return tuple(
        RubricScore(
            dimension=item["dimension"],
            score=int(item["score"]),
            rationale=item["rationale"],
            evidence=tuple(
                EvidenceLink(kind=link["kind"], reference=link["reference"], detail=link.get("detail", ""))
                for link in item.get("evidence", [])
            ),
        )
        for item in payload.get("rubric", [])
    )


def _reproducibility(benchmark: BenchmarkResult) -> RubricScore:
    comparisons = benchmark.comparisons
    if not comparisons:
        return RubricScore(
            dimension="reproducibility",
            score=0,
            rationale="no quantitative reproduction target was extracted to test against",
        )
    within = [c for c in comparisons if c.within_tolerance]
    fraction = len(within) / len(comparisons)
    score = 4 if fraction == 1 else 3 if fraction >= 0.5 else 2 if fraction > 0 else 1
    evidence = tuple(
        EvidenceLink(kind="metric", reference="benchmark/walk_forward.json", detail=c.note)
        for c in comparisons
    )
    rationale = (
        f"{len(within)}/{len(comparisons)} claimed metrics reproduced within tolerance"
    )
    return RubricScore("reproducibility", score, rationale, evidence)


def _robustness(walk_forward: dict[str, Any] | None) -> RubricScore:
    if walk_forward is None:
        return RubricScore("robustness", 0, "no walk-forward evaluation was run")
    n_windows = int(walk_forward.get("n_windows", 0))
    score = 4 if n_windows >= 8 else 3 if n_windows >= 4 else 2 if n_windows >= 2 else 1
    evidence = (
        EvidenceLink(
            kind="artifact",
            reference="benchmark/walk_forward.json",
            detail=f"out-of-sample over {n_windows} purged/embargoed windows",
        ),
    )
    return RubricScore(
        "robustness",
        score,
        f"evaluated out-of-sample across {n_windows} walk-forward windows",
        evidence,
    )


def _net_of_cost_viability(
    benchmark: BenchmarkResult, walk_forward: dict[str, Any] | None
) -> RubricScore:
    if walk_forward is None:
        return RubricScore("net_of_cost_viability", 0, "no net-of-cost benchmark available")
    sharpe = float(benchmark.metrics.get("sharpe", 0.0))
    beats_null = bool(walk_forward.get("beats_random_null", False))
    if beats_null and sharpe >= 1.0:
        score = 4
    elif beats_null and sharpe > 0:
        score = 3
    elif sharpe > 0:
        score = 2
    else:
        score = 1
    evidence = (
        EvidenceLink(
            kind="metric",
            reference="benchmark/walk_forward.json",
            detail=f"net-of-cost annualized Sharpe {sharpe:.2f}; beats random null: {beats_null}",
        ),
    )
    return RubricScore(
        "net_of_cost_viability",
        score,
        f"net-of-cost Sharpe {sharpe:.2f}, "
        + ("beats" if beats_null else "does not beat")
        + " the random-matched-turnover null",
        evidence,
    )


def _novelty_vs_baselines(
    benchmark: BenchmarkResult, walk_forward: dict[str, Any] | None
) -> RubricScore:
    if walk_forward is None or not benchmark.baselines:
        return RubricScore("novelty_vs_baselines", 0, "no baseline suite to compare against")
    candidate = float(benchmark.metrics.get("sharpe", 0.0))
    baseline_sharpes = {
        name: float(metrics.get("sharpe", 0.0))
        for name, metrics in benchmark.baselines.items()
    }
    beaten = [name for name, value in baseline_sharpes.items() if candidate > value]
    score = 4 if len(beaten) == len(baseline_sharpes) else 2 if beaten else 1
    evidence = (
        EvidenceLink(
            kind="metric",
            reference="benchmark/walk_forward.json",
            detail=f"candidate Sharpe {candidate:.2f} vs baselines {baseline_sharpes}",
        ),
    )
    return RubricScore(
        "novelty_vs_baselines",
        score,
        f"beats {len(beaten)}/{len(baseline_sharpes)} baselines on Sharpe",
        evidence,
    )


def _data_accessibility(triage: dict[str, Any] | None) -> RubricScore:
    if triage is None:
        return RubricScore("data_accessibility", 0, "no reproducibility triage was run")
    tier = str(triage.get("data_tier", "unknown"))
    tier_score = {"public": 4, "unknown": 2, "vendor": 2, "proprietary": 0}.get(tier, 1)
    evidence = (
        EvidenceLink(
            kind="artifact",
            reference="manifest:reproducibility_triage",
            detail=f"data tier {tier!r}, feasibility {triage.get('feasibility')}",
        ),
    )
    return RubricScore(
        "data_accessibility",
        tier_score,
        f"data tier {tier!r} (feasibility {triage.get('feasibility')})",
        evidence,
    )


def _derive_verdict(
    rubric: tuple[RubricScore, ...],
    walk_forward: dict[str, Any] | None,
    placeholder_used: bool,
) -> str:
    if placeholder_used:
        return VERDICT_SCAFFOLD
    by_dimension = {score.dimension: score.score for score in rubric}
    repro = by_dimension.get("reproducibility", 0)
    beats_null = bool((walk_forward or {}).get("beats_random_null", False))
    if repro >= 3 and beats_null:
        return "promising"
    if beats_null or repro >= 2:
        return "inconclusive"
    return "weak"


def _rubric_dict(score: RubricScore) -> dict[str, Any]:
    return {
        "dimension": score.dimension,
        "score": score.score,
        "rationale": score.rationale,
        "evidence": [
            {"kind": link.kind, "reference": link.reference, "detail": link.detail}
            for link in score.evidence
        ],
    }


def _manifest_payload(ctx: RunContext, skill_name: str) -> dict[str, Any] | None:
    for result in reversed(ctx.manifest.skill_results):
        if result.skill == skill_name and result.status in ("ok", "skipped"):
            return result.payload
    return None


@register_skill("quant_reviewer", "rubric_verdict")
def _make_rubric_verdict_skill() -> RubricVerdictSkill:
    return RubricVerdictSkill()
