"""QB-24 + QB-26: deflated Sharpe, capacity, multiple-testing correction."""

import math

import pytest

from quantbench_crew.benchmarks.statistics import (
    benjamini_hochberg,
    bonferroni,
    deflated_sharpe_ratio,
    estimate_capacity,
    moments,
    probabilistic_sharpe_ratio,
)

# Positive-mean, nonzero-variance monthly series (deterministic).
POSITIVE = [0.012 + 0.02 * math.sin(i) for i in range(60)]
NOISE = [0.02 * math.sin(i * 1.3) for i in range(60)]  # ~zero mean
TRIALS = [1.2, 0.4, -0.2, 0.7, 0.1]  # dispersed trial Sharpes


def test_moments_basic() -> None:
    mean, std, skew, kurt = moments([1.0, 2.0, 3.0, 4.0, 5.0])
    assert mean == pytest.approx(3.0)
    assert std > 0
    assert abs(skew) < 1e-9  # symmetric


def test_psr_increases_with_sharpe() -> None:
    low = probabilistic_sharpe_ratio(0.1, 0.0, 60, 0.0, 3.0)
    high = probabilistic_sharpe_ratio(0.4, 0.0, 60, 0.0, 3.0)
    assert 0.0 <= low < high <= 1.0


def test_deflated_haircut_grows_with_trial_count() -> None:
    one = deflated_sharpe_ratio(POSITIVE, "monthly", n_trials=1, trial_sharpes=TRIALS)
    many = deflated_sharpe_ratio(POSITIVE, "monthly", n_trials=100, trial_sharpes=TRIALS)

    assert one.observed_sharpe == pytest.approx(many.observed_sharpe)
    # A wider search haircuts harder: deflated falls, haircut grows.
    assert many.deflated_sharpe < one.deflated_sharpe
    assert many.haircut > one.haircut
    assert many.p_value > one.p_value


def test_noise_series_is_not_significant() -> None:
    deflated = deflated_sharpe_ratio(NOISE, "monthly", n_trials=50, trial_sharpes=TRIALS)
    # Near-zero Sharpe across many trials should not look real.
    assert deflated.p_value > 0.5
    assert deflated.deflated_sharpe < 0.5


def test_zero_variance_returns_safe_default() -> None:
    deflated = deflated_sharpe_ratio([0.01] * 20, "monthly", n_trials=5)
    assert deflated.deflated_sharpe == 0.0
    assert deflated.p_value == 1.0


def test_capacity_with_and_without_volume() -> None:
    with_vol = estimate_capacity(0.5, median_dollar_vol=1_000_000_000.0)
    assert with_vol.capacity_usd is not None and with_vol.capacity_usd > 0
    assert with_vol.adv_participation == pytest.approx(0.5)

    without = estimate_capacity(0.5, None)
    assert without.capacity_usd is None
    assert without.notes  # explains why it could not be estimated


def test_benjamini_hochberg_and_bonferroni() -> None:
    pvalues = [0.001, 0.04, 0.5, 0.20]
    bh_passed, bh_threshold = benjamini_hochberg(pvalues, alpha=0.05)
    assert bh_passed[0] is True  # clearly significant
    assert bh_passed[2] is False  # clearly not
    assert bh_threshold <= 0.05

    bonf_passed, bonf_threshold = bonferroni(pvalues, alpha=0.05)
    assert bonf_threshold == pytest.approx(0.05 / 4)
    assert bonf_passed[0] is True
    assert bonf_passed[1] is False  # 0.04 > 0.0125
