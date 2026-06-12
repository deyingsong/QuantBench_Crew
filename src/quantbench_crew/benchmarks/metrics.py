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


def percentile(values: Sequence[float], q: float) -> float:
    """Linear-interpolation percentile, q in [0, 1] (pure Python)."""

    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = q * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def downside_deviation(returns: Sequence[float], target: float = 0.0) -> float:
    """Root-mean-square of returns below ``target`` (Sortino denominator)."""

    if not returns:
        return 0.0
    shortfalls = [min(0.0, r - target) for r in returns]
    return sqrt(sum(s * s for s in shortfalls) / len(returns))


def sortino_ratio(returns: Sequence[float], frequency: str) -> float:
    """Annualized mean over downside deviation (target 0)."""

    downside = downside_deviation(returns)
    if downside == 0.0:
        return 0.0
    mean = sum(returns) / len(returns)
    return mean / downside * sqrt(periods_per_year(frequency))


def calmar_ratio(returns: Sequence[float], frequency: str) -> float:
    """Annualized return over absolute maximum drawdown."""

    drawdown = abs(max_drawdown(returns))
    annual = annualized_return(returns, frequency)
    if drawdown == 0.0:
        return float("inf") if annual > 0 else 0.0
    return annual / drawdown


def expected_shortfall(returns: Sequence[float], alpha: float = 0.05) -> float:
    """CVaR: mean loss in the worst ``alpha`` tail, as a positive number."""

    if not returns:
        return 0.0
    ordered = sorted(returns)
    tail_count = max(1, int(len(ordered) * alpha))
    return -(sum(ordered[:tail_count]) / tail_count)


def directional_accuracy(returns: Sequence[float]) -> float:
    """Hit rate: fraction of periods with a strictly positive return."""

    if not returns:
        return 0.0
    return sum(1 for r in returns if r > 0) / len(returns)


def profit_factor(returns: Sequence[float]) -> float:
    """Sum of gains over absolute sum of losses."""

    gains = sum(r for r in returns if r > 0)
    losses = -sum(r for r in returns if r < 0)
    if losses == 0.0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def tail_ratio(returns: Sequence[float], q: float = 0.05) -> float:
    """|right tail| / |left tail| at the q / 1-q percentiles."""

    left = abs(percentile(returns, q))
    right = abs(percentile(returns, 1.0 - q))
    if left == 0.0:
        return float("inf") if right > 0 else 0.0
    return right / left


def total_pnl(returns: Sequence[float]) -> float:
    """Cumulative simple PnL of a unit-notional book (sum of period returns)."""

    return sum(returns)


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
        "calmar_ratio": calmar_ratio(returns, frequency),
        "sortino_ratio": sortino_ratio(returns, frequency),
        "expected_shortfall": expected_shortfall(returns),
        "directional_accuracy": directional_accuracy(returns),
        "profit_factor": profit_factor(returns),
        "tail_ratio": tail_ratio(returns),
    }
