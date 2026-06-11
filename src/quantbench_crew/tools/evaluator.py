"""Benchmark metric helpers.

Thin compatibility wrapper over :mod:`quantbench_crew.benchmarks.metrics`;
the frequency-aware implementations live there. ``frequency`` defaults to
``"daily"`` so existing placeholder callers keep their sqrt(252) annualization
while the walk-forward harness annualizes by the real data frequency.
"""

from __future__ import annotations

from quantbench_crew.benchmarks.metrics import (
    annualized_sharpe,
    max_drawdown,
    sample_std,
)


def evaluate_returns(returns: list[float], frequency: str = "daily") -> dict[str, float]:
    """Evaluate simple return-series metrics, annualized at ``frequency``."""

    if not returns:
        raise ValueError("Cannot evaluate an empty return series.")

    return {
        "mean_return": sum(returns) / len(returns),
        "volatility": sample_std(returns),
        "sharpe": annualized_sharpe(returns, frequency),
        "max_drawdown": max_drawdown(returns),
    }
