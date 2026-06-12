"""Extended metric suite: hand-computed values, aliases, position stats."""

import math

import pytest

from quantbench_crew.benchmarks.claims import (
    compare_claim,
    normalize_metric_name,
    unmapped_claims,
)
from quantbench_crew.benchmarks.metrics import (
    calmar_ratio,
    directional_accuracy,
    downside_deviation,
    evaluate_series,
    expected_shortfall,
    percentile,
    profit_factor,
    sortino_ratio,
    tail_ratio,
    total_pnl,
)
from quantbench_crew.benchmarks.protocols import (
    WALK_FORWARD_METRIC_KEYS,
    evaluate_walk_forward,
    run_walk_forward,
    walk_forward_windows,
)
from quantbench_crew.benchmarks.reference_momentum import build_strategy
from quantbench_crew.datasets import synthetic
from quantbench_crew.models import Claim, Paper, ReproductionTarget

SERIES = [0.05, -0.02, 0.03, -0.01]  # monthly; hand-computed expectations below


def test_hand_computed_metric_values() -> None:
    assert calmar_ratio(SERIES, "monthly") == pytest.approx(0.15 / 0.02)
    assert expected_shortfall(SERIES) == pytest.approx(0.02)  # worst of 4
    assert directional_accuracy(SERIES) == pytest.approx(0.5)
    assert profit_factor(SERIES) == pytest.approx(0.08 / 0.03)
    assert total_pnl(SERIES) == pytest.approx(0.05)
    assert downside_deviation(SERIES) == pytest.approx(math.sqrt(0.0005 / 4))
    assert sortino_ratio(SERIES, "monthly") == pytest.approx(
        0.0125 / math.sqrt(0.0005 / 4) * math.sqrt(12)
    )
    # percentile interpolation: sorted [-0.02, -0.01, 0.03, 0.05]
    assert percentile(SERIES, 0.05) == pytest.approx(-0.0185)
    assert percentile(SERIES, 0.95) == pytest.approx(0.047)
    assert tail_ratio(SERIES) == pytest.approx(0.047 / 0.0185)


def test_degenerate_guards() -> None:
    all_gains = [0.01, 0.02, 0.03]
    assert profit_factor(all_gains) == float("inf")
    assert calmar_ratio(all_gains, "monthly") == float("inf")
    assert sortino_ratio(all_gains, "monthly") == 0.0  # no downside
    assert profit_factor([-0.01]) == pytest.approx(0.0)
    assert directional_accuracy([]) == 0.0
    assert expected_shortfall([]) == 0.0


def test_evaluate_series_includes_extended_keys() -> None:
    metrics = evaluate_series(SERIES, "monthly")
    for key in (
        "calmar_ratio", "sortino_ratio", "expected_shortfall",
        "directional_accuracy", "profit_factor", "tail_ratio",
    ):
        assert key in metrics


# --- claim aliases: every requested metric name resolves -----------------------

ACHIEVED = {
    "annualized_return": 0.12,
    "calmar_ratio": 1.5,
    "expected_shortfall": 0.03,
    "directional_accuracy": 0.55,
    "gross_pnl": 0.40,
    "net_pnl": 0.35,
    "profit_factor": 1.8,
    "sortino_ratio": 2.0,
    "max_drawdown": -0.10,
    "tail_ratio": 1.2,
    "average_turnover": 0.9,
}


@pytest.mark.parametrize(
    ("paper_name", "expected"),
    [
        ("Annualized Return", 0.12),
        ("Calmar Ratio", 1.5),
        ("Expected Shortfall", 0.03),
        ("CVaR", 0.03),
        ("Directional Accuracy", 0.55),
        ("Hit Rate", 0.55),
        ("Gross PnL", 0.40),
        ("Net PnL", 0.35),
        ("PnL", 0.35),
        ("Profit Factor", 1.8),
        ("Sortino Ratio", 2.0),
        ("Maximum Drawdown", -0.10),
        ("MDD", -0.10),
        ("Tail Ratio", 1.2),
        ("Turnover", 0.9),
    ],
)
def test_every_requested_metric_is_claim_comparable(paper_name, expected) -> None:
    claim = Claim(metric=paper_name, value=expected, tolerance=0.2)
    comparison = compare_claim(claim, ACHIEVED)
    assert comparison.within_tolerance, comparison.note


def test_direct_key_fallback_covers_synthesized_metrics() -> None:
    claim = Claim(metric="Omega Ratio", value=1.4, tolerance=0.2)
    assert not compare_claim(claim, ACHIEVED).within_tolerance  # unmapped
    assert compare_claim(claim, {**ACHIEVED, "omega_ratio": 1.45}).within_tolerance


def test_normalize_and_unmapped_claims() -> None:
    assert normalize_metric_name("  Omega Ratio ") == "omega_ratio"
    assert normalize_metric_name("risk-adjusted return") == "risk_adjusted_return"

    paper = Paper(title="t", abstract="a")
    target = ReproductionTarget(
        paper=paper,
        claims=(
            Claim(metric="sharpe", value=1.0),
            Claim(metric="omega ratio", value=1.4),
        ),
    )
    probe = {key: 0.0 for key in WALK_FORWARD_METRIC_KEYS}
    missing = unmapped_claims(target, probe)
    assert [claim.metric for claim in missing] == ["omega ratio"]


# --- position distribution + PnL through the walk-forward ----------------------

def test_walk_forward_reports_positions_and_pnl() -> None:
    panel = synthetic.planted_momentum(seed=0, n_assets=20)
    windows = walk_forward_windows(panel.dates(), 36, 12, purge=7, embargo=1)
    result = run_walk_forward(build_strategy({"fraction": 0.3}), panel, windows, cost_bps=10.0)
    metrics = evaluate_walk_forward(result, "monthly")

    # fraction 0.3 of 20 assets => 6 long + 6 short every period.
    assert metrics["avg_long_positions"] == pytest.approx(6.0)
    assert metrics["avg_short_positions"] == pytest.approx(6.0)
    assert metrics["avg_positions"] == pytest.approx(12.0)
    assert 0 < metrics["position_concentration"] <= 1.0
    # costs are positive here, so net PnL strictly below gross PnL.
    assert metrics["net_pnl"] < metrics["gross_pnl"]
    assert metrics["net_pnl"] == pytest.approx(sum(result.net_returns))


def test_empty_walk_forward_has_all_metric_keys() -> None:
    panel = synthetic.planted_momentum(seed=0, n_periods=10)  # too short for windows
    result = run_walk_forward(build_strategy(), panel, [], cost_bps=10.0)
    metrics = evaluate_walk_forward(result, "monthly")

    assert set(metrics) == set(WALK_FORWARD_METRIC_KEYS)
    assert all(value == 0.0 for value in metrics.values())
