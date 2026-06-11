"""Walk-forward evaluation skill: candidate vs baselines, claims, metrics.

Runs the reference momentum strategy and the baseline suite through the
purged/embargoed walk-forward on the loaded dataset, computes frequency-aware
net-of-cost metrics, and claim-compares against the paper's reproduction
target. For Phase 1 the evaluated strategy is the trusted reference momentum
implementation parameterized by the extracted MethodSpec; running sandboxed
*generated* strategies through the harness is a later step.

The candidate is judged against ``random_matched_turnover`` — the
significance floor — and the verdict (``beats_random_null``) plus every
metric and claim comparison are recorded in the manifest.
"""

from __future__ import annotations

from typing import Any

from quantbench_crew.artifacts import ArtifactStore
from quantbench_crew.benchmarks import reference_momentum
from quantbench_crew.benchmarks.baselines import build_baselines
from quantbench_crew.benchmarks.claims import compare_claims
from quantbench_crew.benchmarks.protocols import (
    evaluate_walk_forward,
    run_walk_forward,
    walk_forward_windows,
)
from quantbench_crew.datasets.registry import LoadedDataset
from quantbench_crew.models import MethodSpec
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings

DEFAULTS = {
    "train_periods": 36,
    "test_periods": 12,
    "embargo": 1,
    "cost_bps": 10.0,
}


class WalkForwardSkill:
    """Evaluate the candidate strategy and baselines, compare to claims."""

    name = "walk_forward"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        dataset: LoadedDataset = inputs["dataset"]
        spec: MethodSpec | None = inputs.get("spec")
        target = inputs.get("target")
        settings = skill_settings(ctx.config, "quant_bench", self.name)

        params = _strategy_params(spec)
        train_periods = int(settings.get("train_periods", DEFAULTS["train_periods"]))
        test_periods = int(settings.get("test_periods", DEFAULTS["test_periods"]))
        embargo = int(settings.get("embargo", DEFAULTS["embargo"]))
        cost_bps = float(settings.get("cost_bps", DEFAULTS["cost_bps"]))
        # Purge the holding-period overlap between train and test.
        purge = params["formation_periods"] + params["skip_periods"]

        windows = walk_forward_windows(
            dataset.panel.dates(), train_periods, test_periods, purge=purge, embargo=embargo
        )

        candidate_metrics = self._evaluate(
            reference_momentum.build_strategy(params), dataset, windows, cost_bps
        )
        baseline_metrics = {
            name: self._evaluate(strategy, dataset, windows, cost_bps)
            for name, strategy in build_baselines(params).items()
        }

        null_sharpe = baseline_metrics["random_matched_turnover"]["sharpe"]
        beats_null = candidate_metrics["sharpe"] > null_sharpe
        comparisons = compare_claims(target, candidate_metrics)

        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        store.write_json(
            "benchmark/walk_forward.json",
            {
                "dataset": dataset.name,
                "frequency": dataset.frequency,
                "n_windows": len(windows),
                "candidate": candidate_metrics,
                "baselines": baseline_metrics,
                "beats_random_null": beats_null,
                "comparisons": [_comparison_dict(comparison) for comparison in comparisons],
            },
        )

        status = "ok" if windows else "skipped"
        result = SkillResult(
            skill=self.name,
            status=status,
            payload={
                "dataset": dataset.name,
                "frequency": dataset.frequency,
                "metrics": candidate_metrics,
                "baselines": baseline_metrics,
                "beats_random_null": beats_null,
                "comparisons": [_comparison_dict(comparison) for comparison in comparisons],
                "n_windows": len(windows),
            },
            artifacts=("benchmark/walk_forward.json",),
            notes=(
                f"{len(windows)} walk-forward windows on {dataset.name!r}",
                f"candidate sharpe {candidate_metrics['sharpe']:.3f} vs random null "
                f"{null_sharpe:.3f}: {'beats' if beats_null else 'does not beat'} the floor",
            ),
        )
        ctx.manifest.record_skill(result)
        return result

    def _evaluate(self, strategy, dataset, windows, cost_bps) -> dict[str, float]:
        result = run_walk_forward(
            strategy, dataset.panel, windows, cost_bps=cost_bps
        )
        return evaluate_walk_forward(result, dataset.frequency)


def _strategy_params(spec: MethodSpec | None) -> dict[str, Any]:
    hyperparameters = spec.hyperparameters if spec is not None else {}
    return {
        "formation_periods": int(hyperparameters.get("formation_months", 6)),
        "skip_periods": 1,
        "fraction": 0.3,
        "field": "return",
        "seed": 0,
    }


def _comparison_dict(comparison) -> dict[str, Any]:
    claim = comparison.claim
    return {
        "metric": claim.metric,
        "value": claim.value,
        "unit": claim.unit,
        "context": claim.context,
        "tolerance": claim.tolerance,
        "source": claim.source,
        "achieved": comparison.achieved,
        "within_tolerance": comparison.within_tolerance,
        "note": comparison.note,
    }


@register_skill("quant_bench", "walk_forward")
def _make_walk_forward_skill() -> WalkForwardSkill:
    return WalkForwardSkill()
