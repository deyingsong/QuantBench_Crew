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
        deflated = (walk_forward or {}).get("deflated_sharpe")
        robustness = (walk_forward or {}).get("robustness")

        placeholder_used = walk_forward is None or any(
            "placeholder" in note.lower() for note in benchmark.notes
        )

        rubric = (
            _reproducibility(benchmark),
            _robustness(robustness),
            _net_of_cost_viability(benchmark, walk_forward, deflated),
            _novelty_vs_baselines(benchmark, walk_forward),
            _data_accessibility(triage),
        )
        red_team = _red_team(analysis)

        verdict = _derive_verdict(
            rubric, walk_forward, deflated, robustness, red_team, placeholder_used
        )
        strengths = tuple(
            f"{score.dimension}: {score.rationale}"
            for score in rubric
            if score.score >= 3
        ) or ("No dimension scored strongly enough to call a strength.",)
        weaknesses = tuple(
            f"{score.dimension}: {score.rationale}"
            for score in rubric
            if score.score <= 1
        ) + tuple(
            f"red flag [{item['severity']}] {item['kind']}: {item['rationale']}"
            for item in red_team
        )
        if not weaknesses:
            weaknesses = ("No dimension scored a clear weakness.",)

        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={
                "verdict": verdict,
                "placeholder_used": placeholder_used,
                "rubric": [_rubric_dict(score) for score in rubric],
                "strengths": list(strengths),
                "weaknesses": list(weaknesses),
                "red_team": red_team,
            },
            notes=(
                f"verdict {verdict!r}"
                + (" (placeholder data present)" if placeholder_used else ""),
                f"{len(red_team)} red flag(s); robustness sign-stable="
                f"{bool((robustness or {}).get('sign_stable', False))}",
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


def _robustness(robustness: dict[str, Any] | None) -> RubricScore:
    if not robustness:
        return RubricScore("robustness", 0, "no robustness analysis was run")
    sign_stable = bool(robustness.get("sign_stable"))
    subsamples = robustness.get("subsample_sharpes", {})
    spread = float(robustness.get("parameter_sensitivity", {}).get("spread", 0.0))
    if sign_stable and spread < 1.0:
        score = 4
    elif sign_stable:
        score = 3
    elif subsamples:
        score = 1
    else:
        score = 0
    evidence = (
        EvidenceLink(
            kind="artifact",
            reference="benchmark/walk_forward.json",
            detail=f"subsample sharpes {subsamples}; parameter-sweep spread {spread:.2f}",
        ),
    )
    rationale = (
        ("sign-stable" if sign_stable else "sign-UNSTABLE")
        + f" across subsamples; parameter-sweep Sharpe spread {spread:.2f}"
    )
    return RubricScore("robustness", score, rationale, evidence)


def _net_of_cost_viability(
    benchmark: BenchmarkResult,
    walk_forward: dict[str, Any] | None,
    deflated: dict[str, Any] | None,
) -> RubricScore:
    if walk_forward is None:
        return RubricScore("net_of_cost_viability", 0, "no net-of-cost benchmark available")
    sharpe = float(benchmark.metrics.get("sharpe", 0.0))
    beats_null = bool(walk_forward.get("beats_random_null", False))
    p_value = float((deflated or {}).get("p_value", 1.0))
    dsr = float((deflated or {}).get("deflated_sharpe", 0.0))
    survives = p_value < 0.05 and dsr > 0.0
    if beats_null and survives and sharpe >= 1.0:
        score = 4
    elif beats_null and survives:
        score = 3
    elif beats_null and sharpe > 0:
        score = 2
    else:
        score = 1
    evidence = (
        EvidenceLink(
            kind="metric",
            reference="benchmark/walk_forward.json",
            detail=(
                f"net Sharpe {sharpe:.2f}; deflated {dsr:.2f} (p={p_value:.3f}); "
                f"beats random null: {beats_null}"
            ),
        ),
    )
    return RubricScore(
        "net_of_cost_viability",
        score,
        f"net Sharpe {sharpe:.2f}; deflated {dsr:.2f} (p={p_value:.3f}) "
        + ("survives" if survives else "does not survive")
        + " multiple testing; "
        + ("beats" if beats_null else "does not beat")
        + " the random null",
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


def _red_team(analysis: PaperAnalysis) -> list[dict[str, Any]]:
    """The quant-pitfalls checklist, auto-filled from the reader's red flags."""

    return [
        {
            "kind": flag.kind,
            "severity": flag.severity,
            "rationale": flag.rationale,
            "evidence": [
                {"kind": link.kind, "reference": link.reference, "detail": link.detail}
                for link in flag.evidence
            ],
        }
        for flag in analysis.red_flags
    ]


def _derive_verdict(
    rubric: tuple[RubricScore, ...],
    walk_forward: dict[str, Any] | None,
    deflated: dict[str, Any] | None,
    robustness: dict[str, Any] | None,
    red_team: list[dict[str, Any]],
    placeholder_used: bool,
) -> str:
    if placeholder_used:
        return VERDICT_SCAFFOLD
    by_dimension = {score.dimension: score.score for score in rubric}
    repro = by_dimension.get("reproducibility", 0)
    beats_null = bool((walk_forward or {}).get("beats_random_null", False))
    survives = (
        float((deflated or {}).get("p_value", 1.0)) < 0.05
        and float((deflated or {}).get("deflated_sharpe", 0.0)) > 0.0
    )
    sign_stable = bool((robustness or {}).get("sign_stable", False))
    has_critical = any(item["severity"] == "critical" for item in red_team)

    # "Promising" must clear every bar: reproduces, beats the null, survives
    # the multiple-testing deflation, is sign-stable, and carries no critical
    # red flag. Any one failing drops it to inconclusive.
    if repro >= 3 and beats_null and survives and sign_stable and not has_critical:
        return "promising"
    if (beats_null or repro >= 2) and not has_critical:
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
