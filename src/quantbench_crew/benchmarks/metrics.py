"""Frequency-aware performance metrics and a linear cost model.

Annualization scales by the actual data frequency rather than a hard-coded
sqrt(252): monthly momentum data annualizes with sqrt(12), not sqrt(252).
Getting this wrong inflates a monthly strategy's Sharpe by ~4.6x, which is
exactly the kind of unforced error a reproduction harness exists to catch.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import sqrt

PERIODS_PER_YEAR = {"daily": 252.0, "weekly": 52.0, "monthly": 12.0, "annual": 1.0}


def periods_per_year(frequency: str) -> float:
    try:
        return PERIODS_PER_YEAR[frequency]
    except KeyError:
        raise ValueError(
            f"unknown frequency {frequency!r}; expected one of "
            f"{sorted(PERIODS_PER_YEAR)}"
        ) from None


def sample_std(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return sqrt(variance)


def max_drawdown(returns: Sequence[float]) -> float:
    equity = 1.0
    peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        worst = min(worst, (equity / peak) - 1.0)
    return worst


def annualized_sharpe(returns: Sequence[float], frequency: str) -> float:
    volatility = sample_std(returns)
    if volatility == 0.0:
        return 0.0
    mean = sum(returns) / len(returns)
    return mean / volatility * sqrt(periods_per_year(frequency))


def annualized_return(returns: Sequence[float], frequency: str) -> float:
    if not returns:
        return 0.0
    mean = sum(returns) / len(returns)
    return mean * periods_per_year(frequency)


def apply_linear_costs(
    gross_returns: Sequence[float],
    turnovers: Sequence[float],
    cost_bps: float,
) -> list[float]:
    """Subtract turnover * per-unit cost from each gross return.

    ``cost_bps`` is basis points charged per unit of (two-sided) turnover, so
    a fully reversed unit-gross position at 10 bps costs 0.001 of return.
    """

    rate = cost_bps / 10_000.0
    return [gross - turnover * rate for gross, turnover in zip(gross_returns, turnovers)]


def evaluate_series(
    returns: Sequence[float], frequency: str = "monthly"
) -> dict[str, float]:
    """Core return-series metrics, annualized at the given frequency."""

    if not returns:
        raise ValueError("Cannot evaluate an empty return series.")
    return {
        "mean_return": sum(returns) / len(returns),
        "volatility": sample_std(returns),
        "sharpe": annualized_sharpe(returns, frequency),
        "annualized_return": annualized_return(returns, frequency),
        "max_drawdown": max_drawdown(returns),
    }
