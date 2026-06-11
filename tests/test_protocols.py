"""QB-13 acceptance: walk-forward, baselines, frequency-aware metrics.

Headline criterion: the reference momentum strategy beats the random null on
the planted-momentum world and does not on the pure-noise world. Checked
across seeds so the conclusion is statistical, not a single lucky draw.
"""

import pytest

from quantbench_crew.benchmarks.baselines import (
    EqualWeightStrategy,
    RandomMatchedTurnoverStrategy,
    build_baselines,
)
from quantbench_crew.benchmarks.metrics import annualized_sharpe, evaluate_series, periods_per_year
from quantbench_crew.benchmarks.protocols import (
    evaluate_walk_forward,
    run_walk_forward,
    walk_forward_windows,
)
from quantbench_crew.benchmarks.reference_momentum import build_strategy
from quantbench_crew.datasets import synthetic

PARAMS = {"formation_periods": 6, "skip_periods": 1, "fraction": 0.3, "field": "return", "seed": 0}


def _windows(panel):
    return walk_forward_windows(panel.dates(), train_periods=36, test_periods=12, purge=7, embargo=1)


def _candidate_metrics(panel):
    windows = _windows(panel)
    result = run_walk_forward(build_strategy(PARAMS), panel, windows, cost_bps=10.0)
    return evaluate_walk_forward(result, "monthly")


def _random_metrics(panel):
    windows = _windows(panel)
    result = run_walk_forward(
        RandomMatchedTurnoverStrategy(PARAMS), panel, windows, cost_bps=10.0
    )
    return evaluate_walk_forward(result, "monthly")


# --- frequency-aware metrics -------------------------------------------------

def test_periods_per_year_lookup() -> None:
    assert periods_per_year("monthly") == 12.0
    assert periods_per_year("daily") == 252.0
    with pytest.raises(ValueError, match="unknown frequency"):
        periods_per_year("hourly")


def test_annualization_scales_with_frequency() -> None:
    returns = [0.01, -0.005, 0.012, 0.003, -0.002, 0.008]
    monthly = annualized_sharpe(returns, "monthly")
    daily = annualized_sharpe(returns, "daily")

    # Same series, different annualization factors: sqrt(252)/sqrt(12) ~= 4.58.
    assert daily / monthly == pytest.approx((252 / 12) ** 0.5, rel=1e-9)


def test_evaluate_series_rejects_empty() -> None:
    with pytest.raises(ValueError, match="empty return series"):
        evaluate_series([])


# --- walk-forward windows ----------------------------------------------------

def test_walk_forward_windows_apply_purge_and_embargo() -> None:
    panel = synthetic.planted_momentum(n_periods=120)
    dates = panel.dates()
    windows = walk_forward_windows(dates, train_periods=36, test_periods=12, purge=7, embargo=1)

    assert windows
    first = windows[0]
    # purge of 7 leaves 7 periods strictly between train_end and test_start.
    assert dates.index(first.test_start) - dates.index(first.train_end) == 8
    # embargo: next train starts 12 (test) + 1 (embargo) after the prior.
    second = windows[1]
    assert dates.index(second.train_start) - dates.index(first.train_start) == 13
    for window in windows:
        assert window.train_end < window.test_start <= window.test_end


# --- baselines ---------------------------------------------------------------

def test_equal_weight_is_long_only_and_normalized() -> None:
    panel = synthetic.planted_momentum(n_periods=24, n_assets=10)
    weights = EqualWeightStrategy().weights(panel, panel.dates()[-1])

    assert len(weights) == 10
    assert all(w > 0 for w in weights.values())
    assert sum(weights.values()) == pytest.approx(1.0)


def test_random_matched_turnover_is_zero_net_and_deterministic() -> None:
    panel = synthetic.planted_momentum(n_periods=24)
    as_of = panel.dates()[-1]
    first = RandomMatchedTurnoverStrategy(PARAMS).weights(panel, as_of)
    second = RandomMatchedTurnoverStrategy(PARAMS).weights(panel, as_of)

    assert first == second
    assert sum(first.values()) == pytest.approx(0.0)


# --- the headline acceptance criterion --------------------------------------

def test_momentum_beats_random_null_on_planted_world() -> None:
    for seed in range(5):
        panel = synthetic.planted_momentum(seed=seed)
        candidate = _candidate_metrics(panel)
        null = _random_metrics(panel)

        assert candidate["gross_mean_return"] > 0
        assert candidate["sharpe"] > null["sharpe"]
        assert candidate["sharpe"] > 1.0  # a real, strong signal


def test_momentum_does_not_reproduce_on_noise_world() -> None:
    # False-positive floor: momentum must not look like signal on pure noise.
    false_positives = 0
    for seed in range(10):
        panel = synthetic.pure_noise(seed=seed)
        candidate = _candidate_metrics(panel)
        planted = _candidate_metrics(synthetic.planted_momentum(seed=seed))
        # Noise return is an order of magnitude below the planted signal.
        assert abs(candidate["gross_mean_return"]) < planted["gross_mean_return"] / 3
        if candidate["gross_mean_return"] > 0.002:
            false_positives += 1
    assert false_positives <= 1  # <= 10% false-discovery rate across seeds


def test_baseline_suite_has_expected_members() -> None:
    baselines = build_baselines(PARAMS)
    assert set(baselines) == {"equal_weight", "buy_and_hold", "random_matched_turnover"}


def test_costs_reduce_returns() -> None:
    panel = synthetic.pure_noise(seed=0)
    windows = _windows(panel)
    gross = run_walk_forward(
        RandomMatchedTurnoverStrategy(PARAMS), panel, windows, cost_bps=0.0
    )
    costed = run_walk_forward(
        RandomMatchedTurnoverStrategy(PARAMS), panel, windows, cost_bps=50.0
    )
    assert sum(costed.net_returns) < sum(gross.net_returns)
    assert costed.average_turnover > 0
