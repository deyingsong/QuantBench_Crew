"""Walk-forward evaluation skill: candidate vs baselines, claims, rigor.

Runs the reference momentum strategy and the baseline suite through the
purged/embargoed walk-forward on the loaded dataset, then layers the
statistical rigor that separates signal from overfitting: the deflated Sharpe
ratio (haircut by the manifest's trial count), a capacity proxy, an optional
FF5+momentum spanning regression, and a robustness report (subsample
stability + parameter sensitivity). For Phase 1/2 the evaluated strategy is
the trusted reference momentum implementation parameterized by the extracted
MethodSpec; running sandboxed *generated* strategies through the harness is a
later step.

Every metric, the random-null verdict, the deflated Sharpe, and every claim
comparison are recorded in the manifest.
"""

from __future__ import annotations

from pathlib import Path
from statistics import median
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
from quantbench_crew.benchmarks.robustness import build_robustness_report, robustness_to_dict
from quantbench_crew.benchmarks.spanning import factor_spanning, spanning_to_dict
from quantbench_crew.benchmarks.statistics import (
    capacity_to_dict,
    deflated_sharpe_ratio,
    deflated_to_dict,
    estimate_capacity,
)
from quantbench_crew.datasets.french import FF_FACTOR_NAMES, load_ff_factors
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
    """Evaluate the candidate strategy and baselines with full statistical rigor."""

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
        purge = params["formation_periods"] + params["skip_periods"]
        freq = dataset.frequency

        windows = walk_forward_windows(
            dataset.panel.dates(), train_periods, test_periods, purge=purge, embargo=embargo
        )

        candidate_result = run_walk_forward(
            reference_momentum.build_strategy(params), dataset.panel, windows, cost_bps=cost_bps
        )
        candidate_metrics = evaluate_walk_forward(candidate_result, freq)
        baseline_metrics = {
            name: evaluate_walk_forward(
                run_walk_forward(strategy, dataset.panel, windows, cost_bps=cost_bps), freq
            )
            for name, strategy in build_baselines(params).items()
        }

        null_sharpe = baseline_metrics["random_matched_turnover"]["sharpe"]
        beats_null = candidate_metrics["sharpe"] > null_sharpe
        comparisons = compare_claims(target, candidate_metrics)

        # QB-24/26: deflate the observed Sharpe by the full trial count.
        n_trials = 1 + len(baseline_metrics) + _codegen_trials(ctx)
        trial_sharpes = [candidate_metrics["sharpe"], *(m["sharpe"] for m in baseline_metrics.values())]
        deflated = deflated_sharpe_ratio(
            candidate_result.net_returns, freq, n_trials, trial_sharpes
        )
        # QB-24: capacity proxy from turnover and (if available) median ADV.
        capacity = estimate_capacity(
            candidate_metrics["average_turnover"], _median_dollar_vol(dataset.panel)
        )
        # QB-25: optional factor-spanning regression.
        spanning = self._spanning(candidate_result, settings, freq)
        # QB-27: robustness — subsample stability + parameter sweep.
        robustness = build_robustness_report(
            reference_momentum.build_strategy, dataset.panel, windows, params, freq, cost_bps=cost_bps
        )

        payload = {
            "dataset": dataset.name,
            "frequency": freq,
            "n_windows": len(windows),
            "metrics": candidate_metrics,
            "baselines": baseline_metrics,
            "beats_random_null": beats_null,
            "comparisons": [_comparison_dict(c) for c in comparisons],
            "n_trials": n_trials,
            "deflated_sharpe": deflated_to_dict(deflated),
            "capacity": capacity_to_dict(capacity),
            "spanning": spanning_to_dict(spanning) if spanning is not None else None,
            "robustness": robustness_to_dict(robustness),
        }
        store = ArtifactStore(ctx.run_dir, ctx.manifest)
        store.write_json("benchmark/walk_forward.json", payload)

        result = SkillResult(
            skill=self.name,
            status="ok" if windows else "skipped",
            payload=payload,
            artifacts=("benchmark/walk_forward.json",),
            notes=(
                f"{len(windows)} walk-forward windows on {dataset.name!r}",
                f"candidate sharpe {candidate_metrics['sharpe']:.3f} vs random null "
                f"{null_sharpe:.3f}: {'beats' if beats_null else 'does not beat'} the floor",
                f"deflated sharpe {deflated.deflated_sharpe:.3f} (p={deflated.p_value:.3f}, "
                f"{n_trials} trials); robustness sign-stable={robustness.sign_stable}",
            ),
        )
        ctx.manifest.record_skill(result)
        return result

    def _spanning(self, candidate_result, settings, freq):
        factors_path = settings.get("factors_path")
        if not factors_path or not Path(factors_path).exists():
            return None
        factors = load_ff_factors(factors_path)
        factors_by_ym = {(d.year, d.month): vals for d, vals in factors.items()}
        candidate_by_ym = {
            (d.year, d.month): r
            for r, d in zip(candidate_result.net_returns, candidate_result.return_dates)
        }
        present = [
            name for name in FF_FACTOR_NAMES
            if any(name in vals for vals in factors_by_ym.values())
        ]
        if not present:
            return None
        return factor_spanning(candidate_by_ym, factors_by_ym, present, freq)


def _strategy_params(spec: MethodSpec | None) -> dict[str, Any]:
    hyperparameters = spec.hyperparameters if spec is not None else {}
    return {
        "formation_periods": int(hyperparameters.get("formation_months", 6)),
        "skip_periods": 1,
        "fraction": 0.3,
        "field": "return",
        "seed": 0,
    }


def _codegen_trials(ctx: RunContext) -> int:
    """Generated candidates already evaluated this run count as trials."""

    for result in ctx.manifest.skill_results:
        if result.skill == "code_generation":
            return int(result.payload.get("candidates_evaluated", 0))
    return 0


def _median_dollar_vol(panel) -> float | None:
    values = [
        panel.value(d, asset, "dollar_vol")
        for d in panel.dates()
        for asset in panel.assets()
        if panel.value(d, asset, "dollar_vol") is not None
    ]
    return median(values) if values else None


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
