from datetime import date
from pathlib import Path

from quantbench_crew.models import (
    BenchmarkResult,
    Claim,
    ClaimComparison,
    EvidenceLink,
    ImplementationPlan,
    MethodSpec,
    Paper,
    PaperAnalysis,
    ReproductionTarget,
    ReviewReport,
    RubricScore,
    StrategyArtifact,
)


def _paper() -> Paper:
    return Paper(title="Momentum Everywhere", abstract="Cross-sectional momentum.")


def _analysis(paper: Paper) -> PaperAnalysis:
    return PaperAnalysis(
        paper=paper,
        research_question="Does momentum persist?",
        proposed_method="Decile long-short momentum portfolio.",
        assumptions=("liquidity",),
        datasets=("crsp",),
        metrics=("sharpe",),
        limitations=("survivorship",),
    )


def test_new_evidence_and_claim_models_construct() -> None:
    paper = _paper()
    link = EvidenceLink(kind="paper_quote", reference="Table 3, Panel A")
    claim = Claim(metric="sharpe", value=0.8, unit="annualized", source="Table 3")
    target = ReproductionTarget(paper=paper, claims=(claim,), table_reference="Table 3")
    comparison = ClaimComparison(claim=claim, achieved=0.75, within_tolerance=True)

    assert link.detail == ""
    assert claim.tolerance == 0.2
    assert target.claims[0].metric == "sharpe"
    assert comparison.within_tolerance


def test_method_spec_defaults_and_fields() -> None:
    spec = MethodSpec(
        paper=_paper(),
        universe="US common stocks, price > $5",
        frequency="monthly",
        signal_definition="r(t-12, t-2)",
        portfolio_construction="decile long-short, value-weighted",
        rebalance_frequency="monthly",
        holding_period="1 month, overlapping",
        sample_start=date(1963, 7, 1),
    )

    assert spec.sample_end is None
    assert spec.hyperparameters == {}
    assert spec.extraction_confidence == 0.0
    assert spec.evidence == ()


def test_strategy_artifact_constructs() -> None:
    artifact = StrategyArtifact(
        paper=_paper(),
        code_path=Path("generated/momentum.py"),
        entry_point="build_strategy",
    )

    assert artifact.test_paths == ()
    assert artifact.plan is None
    assert artifact.generation_manifest == {}


def test_existing_models_gain_additive_defaults() -> None:
    paper = _paper()
    analysis = _analysis(paper)
    plan = ImplementationPlan(
        paper=paper, modules=("m",), assumptions=(), tests=("t",), open_questions=()
    )
    result = BenchmarkResult(paper=paper, dataset="sample", metrics={"sharpe": 1.0})
    report = ReviewReport(
        paper=paper,
        analysis=analysis,
        implementation_plan=plan,
        benchmark_result=result,
        verdict="inconclusive",
        strengths=(),
        weaknesses=(),
        open_questions=(),
    )

    assert analysis.method_spec is None
    assert analysis.reproduction_target is None
    assert result.comparisons == ()
    assert report.rubric == ()


def test_rubric_score_carries_evidence() -> None:
    score = RubricScore(
        dimension="reproducibility",
        score=3,
        rationale="Claim reproduced within tolerance.",
        evidence=(EvidenceLink(kind="metric", reference="manifest:sharpe"),),
    )

    assert score.evidence[0].kind == "metric"
