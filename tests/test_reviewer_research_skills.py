from quantbench_crew.agents.reviewer import QuantReviewerAgent
from quantbench_crew.models import (
    BenchmarkResult,
    Claim,
    ClaimComparison,
    CritiqueAssessment,
    ExperimentResult,
    ImplementationPlan,
    MethodSpec,
    Paper,
    PaperAnalysis,
    ReproductionTarget,
    RobustnessAudit,
    StrategyEvaluation,
)
from quantbench_crew.skills import default_registry
from quantbench_crew.skills.reviewer.claims_vs_results import (
    ClaimsVsResultsAnalyzerSkill,
    claims_analysis_from_payload,
)


def _inputs():
    paper = Paper(title="Auditable Alpha", abstract="Tests a cross-sectional signal.")
    reproduced = Claim(metric="sharpe", value=1.0, tolerance=0.2, source="Table 2")
    failed = Claim(metric="mean_return", value=0.02, tolerance=0.2, source="Table 3")
    unevaluated = Claim(metric="max_drawdown", value=-0.1, tolerance=0.2, source="Table 4")
    target = ReproductionTarget(
        paper=paper, claims=(reproduced, failed, unevaluated), table_reference="Tables 2-4"
    )
    spec = MethodSpec(
        paper=paper,
        universe="US equities",
        frequency="monthly",
        signal_definition="rank(feature)",
        portfolio_construction="decile long-short",
        rebalance_frequency="monthly",
        holding_period="one month",
        extraction_confidence=0.4,
    )
    analysis = PaperAnalysis(
        paper=paper,
        research_question="Does the signal predict returns?",
        proposed_method="Monthly decile long-short portfolio.",
        assumptions=("tradable at close",),
        datasets=("CRSP",),
        metrics=("sharpe", "mean_return", "max_drawdown"),
        limitations=("short sample",),
        method_spec=spec,
        reproduction_target=target,
        critique=CritiqueAssessment(
            reader_inferred_threats=("possible timestamp ambiguity",),
            unanswered_questions=("Are delistings included?",),
        ),
    )
    plan = ImplementationPlan(
        paper=paper,
        modules=("signal", "portfolio"),
        assumptions=("monthly fills",),
        tests=("no look-ahead",),
        open_questions=("Which close price is executable?",),
    )
    failed_experiment = ExperimentResult(
        name="noise-null",
        dataset="pure_noise",
        expect_edge=False,
        passed=False,
        metrics={"sharpe": 0.8},
    )
    evaluation = StrategyEvaluation(
        paper=paper,
        experiments=(failed_experiment,),
        passed_all=False,
        pass_rate=0.0,
    )
    audit = RobustnessAudit(
        experiments=(failed_experiment,),
        passed_checks=("trial_count_disclosed",),
        failed_checks=("multi_dataset_expectations",),
        unavailable_checks=("subsample_sign_stability",),
        configuration_hash="abcdef1234567890",
        results_hash="123456abcdef7890",
        robust=False,
        recorded_experiments=1,
        disclosed_local_trials=3,
    )
    benchmark = BenchmarkResult(
        paper=paper,
        dataset="crsp",
        metrics={"sharpe": 0.95, "mean_return": 0.01},
        baselines={"equal_weight": {"sharpe": 0.5}},
        notes=("Walk-forward benchmark.",),
        comparisons=(
            ClaimComparison(
                claim=reproduced,
                achieved=0.95,
                within_tolerance=True,
                note="within tolerance",
            ),
            ClaimComparison(
                claim=failed,
                achieved=0.01,
                within_tolerance=False,
                note="outside tolerance",
            ),
        ),
        strategy_evaluation=evaluation,
        robustness_audit=audit,
    )
    return analysis, plan, benchmark


def test_claims_analyzer_builds_forensic_ledger(make_ctx) -> None:
    analysis, plan, benchmark = _inputs()
    ctx = make_ctx()

    result = ClaimsVsResultsAnalyzerSkill().run(
        ctx,
        analysis=analysis,
        implementation_plan=plan,
        benchmark_result=benchmark,
    )
    claims = claims_analysis_from_payload(result.payload)

    assert [item.status for item in claims.findings] == [
        "reproduced",
        "not_reproduced",
        "not_evaluated",
    ]
    assert claims.reproduced_count == 1
    assert claims.failed_count == 1
    assert claims.unevaluated_count == 1
    assert any("low extraction confidence" in item for item in claims.implementation_issues)
    assert any("Robustness check failed" in item for item in claims.reproducibility_issues)
    assert "review/claims_vs_results.json" in ctx.manifest.artifacts


def test_reviewer_compiles_comprehensive_markdown(make_ctx) -> None:
    analysis, plan, benchmark = _inputs()
    ctx = make_ctx()
    reviewer = QuantReviewerAgent(
        skills={
            name: default_registry.create("quant_reviewer", name)
            for name in ("claims_vs_results_analyzer", "report_compiler")
        }
    )

    report = reviewer.review(analysis, plan, benchmark, ctx=ctx)
    markdown = report.to_markdown()

    assert report.claims_analysis is not None
    assert report.compilation is not None
    assert "## Claims Versus Reproduced Results" in markdown
    assert "## Portfolio And Economic Interpretation" in markdown
    assert "## Expert Lens Review" in markdown
    assert "Lopez de Prado" in markdown
    assert "placeholder returns" not in markdown
    assert "Table 4" in markdown
    assert "This report supports research review only" in markdown
    assert "review/compiled_report.md" in ctx.manifest.artifacts
    assert [item.skill for item in ctx.manifest.skill_results] == [
        "claims_vs_results_analyzer",
        "report_compiler",
    ]
