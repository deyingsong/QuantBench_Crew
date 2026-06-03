import pytest

from quantbench_crew.tools.evaluator import evaluate_returns


def test_evaluate_returns_includes_core_metrics() -> None:
    metrics = evaluate_returns([0.01, -0.005, 0.002])

    assert set(metrics) == {"mean_return", "volatility", "sharpe", "max_drawdown"}
    assert metrics["volatility"] > 0
    assert metrics["max_drawdown"] <= 0


def test_evaluate_returns_rejects_empty_series() -> None:
    with pytest.raises(ValueError, match="empty return series"):
        evaluate_returns([])
