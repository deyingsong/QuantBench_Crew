"""QuantBench agent for benchmark result generation."""

from __future__ import annotations

from collections.abc import Mapping

from quantbench_crew.benchmarks.claims import compare_claims
from quantbench_crew.benchmarks.spanning import spanning_from_dict
from quantbench_crew.benchmarks.statistics import capacity_from_dict, deflated_from_dict
from quantbench_crew.datasets.registry import load_dataset
from quantbench_crew.models import BenchmarkResult, ImplementationPlan, PaperAnalysis
from quantbench_crew.skills.base import RunContext, Skill, skill_settings
from quantbench_crew.skills.bench.robustness_auditor import robustness_audit_from_payload
from quantbench_crew.skills.bench.strategy_evaluator import (
    strategy_evaluation_from_payload,
)
from quantbench_crew.tools.evaluator import evaluate_returns


class QuantBenchAgent:
    """Evaluate a method on benchmark data, real or placeholder."""

    def __init__(self, skills: Mapping[str, Skill] | None = None) -> None:
        self.skills = dict(skills or {})

    def evaluate(
        self,
        plan: ImplementationPlan,
        returns: list[float] | None = None,
        dataset: str = "sample_returns",
        analysis: PaperAnalysis | None = None,
        ctx: RunContext | None = None,
    ) -> BenchmarkResult:
        if ctx is not None and "walk_forward" in self.skills:
            real = self._evaluate_with_skills(plan, analysis, ctx)
            if real is not None:
                return real

        sample_returns = returns or [0.01, -0.004, 0.006, 0.0, 0.012, -0.008, 0.004]
        metrics = evaluate_returns(sample_returns)
        baselines = {
            "zero_return": evaluate_returns([0.0 for _ in sample_returns]),
            "equal_weight_placeholder": evaluate_returns([sum(sample_returns) / len(sample_returns)]),
        }
        return BenchmarkResult(
            paper=plan.paper,
            dataset=dataset,
            metrics=metrics,
            baselines=baselines,
            notes=("Placeholder benchmark data; connect real datasets before drawing conclusions.",),
        )

    def _evaluate_with_skills(
        self,
        plan: ImplementationPlan,
        analysis: PaperAnalysis | None,
        ctx: RunContext,
    ) -> BenchmarkResult | None:
        """Real evaluation: load a dataset, walk-forward, claim-compare."""

        registry_settings = skill_settings(ctx.config, "quant_bench", "dataset_registry")
        dataset_name = registry_settings.get("dataset", "planted_momentum")
        dataset_params = registry_settings.get("params", {})
        loaded = load_dataset(dataset_name, dataset_params)

        registry_skill = self.skills.get("dataset_registry")
        if registry_skill is not None:
            registry_skill.run(ctx, dataset=loaded)

        spec = analysis.method_spec if analysis is not None else None
        target = analysis.reproduction_target if analysis is not None else None
        wf = self.skills["walk_forward"].run(
            ctx, dataset=loaded, spec=spec, target=target
        )

        strategy_evaluation = None
        strategy_payload: dict = {}
        strategy_skill = self.skills.get("strategy_evaluator")
        if strategy_skill is not None:
            strategy_result = strategy_skill.run(
                ctx,
                dataset=loaded,
                spec=spec,
                target=target,
                primary_payload=wf.payload,
            )
            strategy_payload = dict(
                strategy_result.payload.get("strategy_evaluation") or {}
            )
            strategy_evaluation = strategy_evaluation_from_payload(
                plan.paper, strategy_result.payload
            )

        robustness_audit = None
        audit_skill = self.skills.get("robustness_auditor")
        if audit_skill is not None:
            audit_result = audit_skill.run(
                ctx,
                dataset=loaded,
                spec=spec,
                target=target,
                primary_payload=wf.payload,
                strategy_evaluation=strategy_payload,
            )
            robustness_audit = robustness_audit_from_payload(audit_result.payload)

        metrics = {key: float(value) for key, value in wf.payload["metrics"].items()}
        baselines = {
            name: {key: float(value) for key, value in baseline.items()}
            for name, baseline in wf.payload["baselines"].items()
        }
        comparisons = compare_claims(target, metrics)

        deflated = deflated_from_dict(wf.payload.get("deflated_sharpe"))
        capacity = capacity_from_dict(wf.payload.get("capacity"))
        spanning = spanning_from_dict(wf.payload.get("spanning"))

        verdict = "beats random null" if wf.payload["beats_random_null"] else "no edge over random null"
        notes = (
            f"Walk-forward on {loaded.name!r} ({loaded.frequency}, "
            f"{wf.payload['n_windows']} windows); candidate {verdict}.",
        )
        if deflated is not None:
            notes += (
                f"Deflated Sharpe {deflated.deflated_sharpe:.2f} vs observed "
                f"{deflated.observed_sharpe:.2f} over {deflated.n_trials} trials "
                f"(p={deflated.p_value:.3f}).",
            )
        if not comparisons:
            notes += ("No reproduction target to claim-compare against.",)
        return BenchmarkResult(
            paper=plan.paper,
            dataset=loaded.name,
            metrics=metrics,
            baselines=baselines,
            notes=notes,
            comparisons=comparisons,
            deflated_sharpe=deflated,
            capacity=capacity,
            spanning=spanning,
            strategy_evaluation=strategy_evaluation,
            robustness_audit=robustness_audit,
        )
