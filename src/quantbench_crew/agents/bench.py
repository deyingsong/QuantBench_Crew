"""QuantBench agent for benchmark result generation."""

from __future__ import annotations

from quantbench_crew.models import BenchmarkResult, ImplementationPlan
from quantbench_crew.tools.evaluator import evaluate_returns


class QuantBenchAgent:
    """Evaluate a method placeholder on sample benchmark data."""

    def evaluate(
        self,
        plan: ImplementationPlan,
        returns: list[float] | None = None,
        dataset: str = "sample_returns",
    ) -> BenchmarkResult:
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
