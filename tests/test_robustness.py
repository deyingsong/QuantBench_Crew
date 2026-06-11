"""QB-27: subsample stability and parameter sensitivity."""

from quantbench_crew.benchmarks.protocols import walk_forward_windows
from quantbench_crew.benchmarks.reference_momentum import build_strategy
from quantbench_crew.benchmarks.robustness import build_robustness_report
from quantbench_crew.datasets import synthetic

PARAMS = {"formation_periods": 6, "skip_periods": 1, "fraction": 0.3, "field": "return", "seed": 0}


def _report(panel):
    windows = walk_forward_windows(panel.dates(), 36, 12, purge=7, embargo=1)
    return build_robustness_report(build_strategy, panel, windows, PARAMS, "monthly")


def test_reference_momentum_is_sign_stable_on_planted() -> None:
    report = _report(synthetic.planted_momentum(seed=0))

    assert report.sign_stable
    assert len(report.subsample_sharpes) == 2
    assert all(s > 0 for s in report.subsample_sharpes.values())
    assert "spread" in report.parameter_sensitivity


def test_momentum_is_sign_unstable_on_noise() -> None:
    # On pure noise the candidate is a fragile artifact: its sign flips across
    # subsamples, which is exactly what robustness must flag.
    unstable = 0
    for seed in range(5):
        report = _report(synthetic.pure_noise(seed=seed))
        if not report.sign_stable:
            unstable += 1
    assert unstable >= 4  # noise is overwhelmingly not sign-stable


def test_parameter_sensitivity_sweeps_formation() -> None:
    report = _report(synthetic.planted_momentum(seed=1))
    sweep_keys = [k for k in report.parameter_sensitivity if k.startswith("formation_periods=")]
    assert len(sweep_keys) == 4  # default sweep grid (3, 6, 9, 12)
