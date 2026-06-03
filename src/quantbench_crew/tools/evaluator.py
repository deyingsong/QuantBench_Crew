"""Benchmark metric helpers."""

from __future__ import annotations

from math import sqrt


def evaluate_returns(returns: list[float]) -> dict[str, float]:
    """Evaluate simple return-series metrics."""

    if not returns:
        raise ValueError("Cannot evaluate an empty return series.")

    mean_return = sum(returns) / len(returns)
    volatility = _sample_std(returns)
    sharpe = mean_return / volatility * sqrt(252) if volatility else 0.0
    return {
        "mean_return": mean_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": _max_drawdown(returns),
    }


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return sqrt(variance)


def _max_drawdown(returns: list[float]) -> float:
    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        drawdown = (equity / peak) - 1.0
        max_drawdown = min(max_drawdown, drawdown)
    return max_drawdown
