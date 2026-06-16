from datetime import date
from pathlib import Path

from quantbench_crew.models import (
    BenchmarkResult,
    Claim,
    ClaimComparison,
    ClaimResultFinding,
    ClaimsVsResultsAnalysis,
    CritiqueAssessment,
    EmpiricalSpecification,
    EvidenceLink,
    ExperimentResult,
    ImplementationPlan,
    MethodSpec,
    MethodologyAssessment,
    Paper,
    PaperAnalysis,
    ResearchQuestionAssessment,
    ReproductionTarget,
    ReportCompilation,
    RobustnessAudit,
    ReviewReport,
    RubricScore,
    StrategyEvaluation,
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
    assert analysis.question_assessment is None
    assert analysis.methodology_assessment is None
    assert analysis.empirical_spec is None
    assert analysis.critique is None
    assert result.comparisons == ()
    assert result.strategy_evaluation is None
    assert result.robustness_audit is None
    assert report.rubric == ()
    assert report.claims_analysis is None
    assert report.compilation is None


def test_review_markdown_includes_original_paper_link() -> None:
    paper = Paper(
        title="Linked Paper",
        abstract="A paper with a source URL.",
        source="journal",
        url="https://example.org/linked-paper",
    )
    report = ReviewReport(
        paper=paper,
        analysis=_analysis(paper),
        implementation_plan=ImplementationPlan(
            paper=paper,
            modules=("method",),
            assumptions=(),
            tests=(),
            open_questions=(),
        ),
        benchmark_result=BenchmarkResult(paper=paper, dataset="sample", metrics={}),
        verdict="inconclusive",
        strengths=(),
        weaknesses=(),
        open_questions=(),
    )

    assert "**Paper:** [Original paper](https://example.org/linked-paper)" in report.to_markdown()


def test_reader_assessment_models_construct() -> None:
    evidence = (EvidenceLink(kind="paper_quote", reference="abstract"),)

    question = ResearchQuestionAssessment(
        question="Does the method improve forecasts?", evidence=evidence
    )
    methodology = MethodologyAssessment(summary="Estimate a nonlinear model.")
    empirical = EmpiricalSpecification(datasets=("CRSP",), labels=("next-month return",))
    critique = CritiqueAssessment(reader_inferred_threats=("possible leakage",))

    assert question.evidence == evidence
    assert methodology.equations == ()
    assert empirical.datasets == ("CRSP",)
    assert critique.reader_inferred_threats == ("possible leakage",)


def test_bench_evaluation_and_audit_models_construct() -> None:
    paper = _paper()
    experiment = ExperimentResult(
        name="noise-null",
        dataset="pure_noise",
        expect_edge=False,
        passed=True,
        metrics={"sharpe": -0.2},
    )
    evaluation = StrategyEvaluation(
        paper=paper, experiments=(experiment,), passed_all=True, pass_rate=1.0
    )
    audit = RobustnessAudit(
        experiments=(experiment,),
        passed_checks=("noise_rejection",),
        failed_checks=(),
        unavailable_checks=(),
        configuration_hash="config",
        results_hash="results",
        robust=True,
    )

    assert evaluation.experiments[0].passed
    assert audit.robust


def test_rubric_score_carries_evidence() -> None:
    score = RubricScore(
        dimension="reproducibility",
        score=3,
        rationale="Claim reproduced within tolerance.",
        evidence=(EvidenceLink(kind="metric", reference="manifest:sharpe"),),
    )

    assert score.evidence[0].kind == "metric"


def test_reviewer_research_models_construct() -> None:
    finding = ClaimResultFinding(
        metric="sharpe",
        claimed_value=1.0,
        achieved_value=0.7,
        tolerance=0.2,
        status="not_reproduced",
        gap=-0.3,
    )
    analysis = ClaimsVsResultsAnalysis(
        findings=(finding,),
        implementation_issues=("missing lag rule",),
        reproducibility_issues=("cost model unavailable",),
        reproduced_count=0,
        failed_count=1,
        unevaluated_count=0,
    )
    compilation = ReportCompilation(
        executive_summary="inconclusive",
        empirical_findings=("Sharpe 0.7",),
        expert_lens_findings=("Costs unresolved",),
        strengths=(),
        weaknesses=("Claim missed",),
        open_questions=("Which lag rule?",),
        markdown="# Review\n",
    )

    assert analysis.findings[0].gap == -0.3
    assert compilation.markdown == "# Review\n"
