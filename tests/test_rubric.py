"""QB-15 acceptance: evidence-cited rubric; two papers differ; scaffold guard."""

from quantbench_crew.models import (
    BenchmarkResult,
    Claim,
    ClaimComparison,
    Paper,
    PaperAnalysis,
)
from quantbench_crew.skills.base import SkillResult
from quantbench_crew.skills.reviewer.rubric import RubricVerdictSkill


def _analysis(title: str) -> PaperAnalysis:
    paper = Paper(title=title, abstract="abstract")
    return PaperAnalysis(
        paper=paper,
        research_question="q",
        proposed_method="momentum",
        assumptions=(),
        datasets=(),
        metrics=("sharpe",),
        limitations=(),
    )


def _seed_manifest(ctx, *, data_tier: str, beats_null: bool, n_windows: int = 10) -> None:
    ctx.manifest.record_skill(
        SkillResult(
            skill="reproducibility_triage",
            status="ok",
            payload={"data_tier": data_tier, "feasibility": 0.9 if data_tier == "public" else 0.4},
        )
    )
    ctx.manifest.record_skill(
        SkillResult(
            skill="walk_forward",
            status="ok",
            payload={"beats_random_null": beats_null, "n_windows": n_windows},
        )
    )


def _benchmark(within_tolerance: bool, sharpe: float) -> BenchmarkResult:
    claim = Claim(metric="monthly_return", value=0.0095, tolerance=0.2)
    achieved = 0.0095 if within_tolerance else 0.05
    return BenchmarkResult(
        paper=Paper(title="x", abstract=""),
        dataset="planted_momentum",
        metrics={"sharpe": sharpe},
        baselines={"random_matched_turnover": {"sharpe": 0.0}, "equal_weight": {"sharpe": 0.3}},
        notes=("Walk-forward on 'planted_momentum'.",),
        comparisons=(
            ClaimComparison(claim=claim, achieved=achieved, within_tolerance=within_tolerance, note="n"),
        ),
    )


def test_strong_reproduction_scores_promising_with_evidence(make_ctx) -> None:
    ctx = make_ctx()
    _seed_manifest(ctx, data_tier="public", beats_null=True)

    result = RubricVerdictSkill().run(
        ctx, analysis=_analysis("A"), benchmark_result=_benchmark(True, sharpe=2.0)
    )

    assert result.payload["verdict"] == "promising"
    assert result.payload["placeholder_used"] is False
    rubric = {item["dimension"]: item for item in result.payload["rubric"]}
    assert rubric["reproducibility"]["score"] == 4
    assert rubric["data_accessibility"]["score"] == 4
    # Every scored dimension cites an evidence link.
    assert all(item["evidence"] for item in result.payload["rubric"] if item["score"] > 0)


def test_two_papers_produce_different_reports(make_ctx) -> None:
    strong_ctx = make_ctx()
    _seed_manifest(strong_ctx, data_tier="public", beats_null=True)
    strong = RubricVerdictSkill().run(
        strong_ctx, analysis=_analysis("Strong"), benchmark_result=_benchmark(True, 2.0)
    )

    weak_ctx = make_ctx()
    _seed_manifest(weak_ctx, data_tier="vendor", beats_null=False)
    weak = RubricVerdictSkill().run(
        weak_ctx, analysis=_analysis("Weak"), benchmark_result=_benchmark(False, -0.2)
    )

    assert strong.payload["verdict"] != weak.payload["verdict"]
    strong_repro = next(i for i in strong.payload["rubric"] if i["dimension"] == "reproducibility")
    weak_repro = next(i for i in weak.payload["rubric"] if i["dimension"] == "reproducibility")
    assert strong_repro["score"] > weak_repro["score"]
    strong_data = next(i for i in strong.payload["rubric"] if i["dimension"] == "data_accessibility")
    weak_data = next(i for i in weak.payload["rubric"] if i["dimension"] == "data_accessibility")
    assert strong_data["score"] > weak_data["score"]


def test_placeholder_run_is_scaffold_only(make_ctx) -> None:
    ctx = make_ctx()
    # No walk_forward recorded => placeholder; verdict must be scaffold-only
    # even though the metrics look strong.
    placeholder = BenchmarkResult(
        paper=Paper(title="x", abstract=""),
        dataset="sample_returns",
        metrics={"sharpe": 5.0},
        notes=("Placeholder benchmark data; connect real datasets before drawing conclusions.",),
    )

    result = RubricVerdictSkill().run(
        ctx, analysis=_analysis("A"), benchmark_result=placeholder
    )

    assert result.payload["verdict"] == "scaffold-only"
    assert result.payload["placeholder_used"] is True


def test_missing_reproduction_target_scores_zero(make_ctx) -> None:
    ctx = make_ctx()
    _seed_manifest(ctx, data_tier="public", beats_null=True)
    benchmark = BenchmarkResult(
        paper=Paper(title="x", abstract=""),
        dataset="planted_momentum",
        metrics={"sharpe": 1.5},
        notes=("Walk-forward run.",),
        comparisons=(),
    )

    result = RubricVerdictSkill().run(ctx, analysis=_analysis("A"), benchmark_result=benchmark)

    repro = next(i for i in result.payload["rubric"] if i["dimension"] == "reproducibility")
    assert repro["score"] == 0
    # Beats the null, so still informative even without a target.
    assert result.payload["verdict"] == "inconclusive"
