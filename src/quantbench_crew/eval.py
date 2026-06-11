"""The system's own regression harness (QB-33).

Runs each :class:`EvalCase` through the real bench and reviewer skills on its
configured dataset, strategy, and hand-labeled reproduction target, then
compares the achieved verdict to the case's ``expected_outcome``. A case that
should reproduce must earn ``promising`` (the strict bar — reproduces the
claim, beats the random null, survives the deflated-Sharpe correction, is
sign-stable, no critical red flag); a case that should not must earn anything
else. This is what guards against the system silently regressing — including
the meta-risk of tuning the system until noise looks real.
"""

from __future__ import annotations

from pathlib import Path

from quantbench_crew.agents.bench import QuantBenchAgent
from quantbench_crew.agents.reviewer import QuantReviewerAgent
from quantbench_crew.artifacts import start_run
from quantbench_crew.datasets import crsp, french
from quantbench_crew.models import EvalCase, EvalResult, ImplementationPlan, PaperAnalysis
from quantbench_crew.skills import resolve_skills
from quantbench_crew.skills.base import RunContext

DEFAULT_TRAIN_PERIODS = 36
DEFAULT_TEST_PERIODS = 12


def _eval_config(case: EvalCase, train_periods: int, test_periods: int) -> dict:
    return {
        "llm": {"provider": "none"},
        "agents": {
            "quant_bench": {
                "skills": {
                    "dataset_registry": {
                        "enabled": True,
                        "dataset": case.dataset,
                        "params": dict(case.dataset_params),
                    },
                    "walk_forward": {
                        "enabled": True,
                        "strategy": case.strategy,
                        "strategy_params": _strategy_params(case),
                        "train_periods": train_periods,
                        "test_periods": test_periods,
                        "embargo": 1,
                        "cost_bps": 10.0,
                    },
                }
            },
            "quant_reviewer": {"skills": {"rubric_verdict": {"enabled": True}}},
        },
    }


def _strategy_params(case: EvalCase) -> dict:
    # Per-strategy knobs; the bench merges these over the spec defaults.
    if case.strategy == "momentum":
        return {"formation_periods": 6, "skip_periods": 1, "fraction": 0.3}
    if case.strategy == "ml":
        return {"features": ["cap", "std_ret", "max_ret"], "fraction": 0.3}
    if case.strategy == "size":
        return {"fraction": 0.3}
    return {}


def case_available(case: EvalCase) -> bool:
    """Whether the case's data is present (CRSP/French cases need their files)."""

    if case.data_tier == "crsp":
        return Path(crsp.DEFAULT_DAILY_PATH).exists()
    if case.data_tier == "french":
        return Path(french.DEFAULT_FIXTURE).exists()
    return True  # synthetic is always available


def run_eval_case(
    case: EvalCase,
    runs_dir: Path,
    *,
    train_periods: int = DEFAULT_TRAIN_PERIODS,
    test_periods: int = DEFAULT_TEST_PERIODS,
) -> EvalResult:
    """Run one case through bench + reviewer and judge it against expectation."""

    config = _eval_config(case, train_periods, test_periods)
    bench = QuantBenchAgent(skills=resolve_skills("quant_bench", config))
    reviewer = QuantReviewerAgent(skills=resolve_skills("quant_reviewer", config))

    manifest, store = start_run(Path(runs_dir), case.slug, config)
    ctx = RunContext(
        run_id=manifest.run_id,
        run_dir=store.run_dir,
        config=config,
        manifest=manifest,
        llm=None,
    )

    analysis = PaperAnalysis(
        paper=case.paper,
        research_question="",
        proposed_method=case.strategy,
        assumptions=(),
        datasets=(case.data_tier,),
        metrics=("sharpe",),
        limitations=(),
        reproduction_target=case.targets,
    )
    plan = ImplementationPlan(
        paper=case.paper, modules=(), assumptions=(), tests=(), open_questions=()
    )

    benchmark = bench.evaluate(plan, analysis=analysis, ctx=ctx)
    report = reviewer.review(analysis, plan, benchmark, ctx=ctx)
    manifest.save(store.run_dir)

    verdict = report.verdict
    reproduced = verdict == "promising"
    expected_reproduce = case.expected_outcome == "reproduces"
    matches = reproduced == expected_reproduce

    deflated = benchmark.deflated_sharpe
    detail = (
        f"verdict={verdict!r} expected={case.expected_outcome!r}; "
        f"sharpe={benchmark.metrics.get('sharpe', 0.0):.2f}"
        + (
            f"; deflated={deflated.deflated_sharpe:.2f} (p={deflated.p_value:.3f})"
            if deflated is not None
            else ""
        )
    )
    return EvalResult(case=case, achieved_verdict=verdict, matches_expected=matches, detail=detail)


def run_eval_suite(cases: list[EvalCase], runs_dir: Path) -> list[EvalResult]:
    """Run every available case; unavailable-data cases are skipped silently."""

    return [run_eval_case(case, runs_dir) for case in cases if case_available(case)]


def format_report(results: list[EvalResult]) -> str:
    """Markdown regression report for the eval suite."""

    rows = ["| Case | Tier | Expected | Verdict | Pass |", "| --- | --- | --- | --- | :---: |"]
    for r in results:
        mark = "PASS" if r.matches_expected else "FAIL"
        rows.append(
            f"| {r.case.slug} | {r.case.data_tier} | {r.case.expected_outcome} | "
            f"{r.achieved_verdict} | {mark} |"
        )
    passed = sum(1 for r in results if r.matches_expected)
    rows.append("")
    rows.append(f"**{passed}/{len(results)} cases match expectation.**")
    return "\n".join(rows)
