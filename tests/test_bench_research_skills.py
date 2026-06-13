from quantbench_crew.agents.bench import QuantBenchAgent
from quantbench_crew.models import ImplementationPlan, Paper
from quantbench_crew.skills import default_registry


def _config() -> dict:
    return {
        "agents": {
            "quant_bench": {
                "skills": {
                    "dataset_registry": {
                        "dataset": "planted_momentum",
                        "params": {
                            "seed": 0,
                            "strength": 0.02,
                            "noise": 0.0005,
                            "n_periods": 120,
                        },
                    },
                    "walk_forward": {
                        "train_periods": 36,
                        "test_periods": 12,
                        "embargo": 1,
                        "cost_bps": 10.0,
                    },
                    "strategy_evaluator": {
                        "primary_expect_edge": True,
                        "datasets": [
                            {
                                "experiment": "pure-noise-null",
                                "name": "pure_noise",
                                "params": {"seed": 4, "n_periods": 120},
                                "expect_edge": False,
                            }
                        ],
                    },
                    "robustness_auditor": {
                        "cost_bps_scenarios": [10.0, 25.0],
                        "max_parameter_sharpe_spread": 10000.0,
                        "max_deflated_sharpe_p_value": 1.0,
                    },
                }
            }
        }
    }


def _skills():
    return {
        name: default_registry.create("quant_bench", name)
        for name in ("walk_forward", "strategy_evaluator", "robustness_auditor")
    }


def test_bench_attaches_multi_dataset_evaluation_and_audit(make_ctx) -> None:
    paper = Paper(title="Cross-Market Momentum", abstract="A momentum strategy.")
    plan = ImplementationPlan(
        paper=paper, modules=("strategy",), assumptions=(), tests=(), open_questions=()
    )
    ctx = make_ctx(config=_config())

    result = QuantBenchAgent(skills=_skills()).evaluate(plan, ctx=ctx)

    assert result.strategy_evaluation is not None
    assert result.strategy_evaluation.passed_all
    assert result.strategy_evaluation.pass_rate == 1.0
    assert {item.dataset for item in result.strategy_evaluation.experiments} == {
        "planted_momentum",
        "pure_noise",
    }
    noise = next(
        item
        for item in result.strategy_evaluation.experiments
        if item.dataset == "pure_noise"
    )
    assert noise.expect_edge is False
    assert noise.passed

    assert result.robustness_audit is not None
    assert result.robustness_audit.robust
    assert len(result.robustness_audit.experiments) == 4
    assert result.robustness_audit.recorded_experiments == 4
    assert result.robustness_audit.disclosed_local_trials > 0
    assert result.robustness_audit.configuration_hash
    assert result.robustness_audit.results_hash
    assert "benchmark/strategy_evaluation.json" in ctx.manifest.artifacts
    assert "benchmark/robustness_audit.json" in ctx.manifest.artifacts


def test_audit_hashes_are_deterministic(make_ctx) -> None:
    paper = Paper(title="Cross-Market Momentum", abstract="A momentum strategy.")
    plan = ImplementationPlan(
        paper=paper, modules=("strategy",), assumptions=(), tests=(), open_questions=()
    )

    first = QuantBenchAgent(skills=_skills()).evaluate(
        plan, ctx=make_ctx(config=_config())
    ).robustness_audit
    second = QuantBenchAgent(skills=_skills()).evaluate(
        plan, ctx=make_ctx(config=_config())
    ).robustness_audit

    assert first is not None and second is not None
    assert first.configuration_hash == second.configuration_hash
    assert first.results_hash == second.results_hash
