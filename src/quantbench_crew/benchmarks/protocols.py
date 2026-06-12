"""Purged, embargoed walk-forward evaluation.

Sequential walk-forward with two leakage guards from Lopez de Prado's
*Advances in Financial Machine Learning*:

- **purge**: drop ``purge`` periods between each train window and its test
  window, because an overlapping holding period makes the label at the test
  boundary depend on data inside the train window;
- **embargo**: skip ``embargo`` periods after each test window before the next
  fold, so serial correlation across the boundary cannot leak backward.

The harness itself never looks ahead: weights formed at ``t`` are applied to
the return realized at ``t+1``, and every strategy is handed ``data.up_to(t)``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from quantbench_crew.benchmarks.contract import PanelData, Strategy
from quantbench_crew.benchmarks.metrics import apply_linear_costs, evaluate_series, total_pnl


@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: date
    train_end: date
    test_start: date
    test_end: date


@dataclass(frozen=True)
class WalkForwardResult:
    gross_returns: list[float]
    net_returns: list[float]
    turnovers: list[float]
    windows: tuple[WalkForwardWindow, ...]
    return_dates: list[date] = field(default_factory=list)  # realized-return date per return
    long_counts: list[int] = field(default_factory=list)    # positions held per period
    short_counts: list[int] = field(default_factory=list)
    max_weights: list[float] = field(default_factory=list)  # max |w| per period

    @property
    def average_turnover(self) -> float:
        return sum(self.turnovers) / len(self.turnovers) if self.turnovers else 0.0

    def position_distribution(self) -> dict[str, float]:
        """Scalar summary of the per-period position distribution."""

        n = len(self.long_counts)
        if n == 0:
            return {
                "avg_positions": 0.0,
                "avg_long_positions": 0.0,
                "avg_short_positions": 0.0,
                "position_concentration": 0.0,
            }
        longs = sum(self.long_counts) / n
        shorts = sum(self.short_counts) / n
        return {
            "avg_positions": longs + shorts,
            "avg_long_positions": longs,
            "avg_short_positions": shorts,
            "position_concentration": sum(self.max_weights) / n,
        }


def walk_forward_windows(
    dates: tuple[date, ...],
    train_periods: int,
    test_periods: int,
    purge: int = 0,
    embargo: int = 0,
) -> list[WalkForwardWindow]:
    """Build sequential train/test windows with purge and embargo gaps."""

    windows: list[WalkForwardWindow] = []
    start = 0
    n = len(dates)
    while True:
        train_end_idx = start + train_periods
        test_start_idx = train_end_idx + purge
        test_end_idx = test_start_idx + test_periods
        if test_end_idx > n:
            break
        windows.append(
            WalkForwardWindow(
                train_start=dates[start],
                train_end=dates[train_end_idx - 1],
                test_start=dates[test_start_idx],
                test_end=dates[test_end_idx - 1],
            )
        )
        start += test_periods + embargo
    return windows


def run_walk_forward(
    strategy: Strategy,
    data: PanelData,
    windows: list[WalkForwardWindow],
    return_field: str = "return",
    cost_bps: float = 10.0,
) -> WalkForwardResult:
    """Refit per window, rebalance each test period, collect OOS returns."""

    dates = data.dates()
    index = {d: i for i, d in enumerate(dates)}

    gross_returns: list[float] = []
    turnovers: list[float] = []
    return_dates: list[date] = []
    long_counts: list[int] = []
    short_counts: list[int] = []
    max_weights: list[float] = []
    prev_weights: dict[str, float] = {}

    for window in windows:
        strategy.fit(data.up_to(window.train_end), window.train_end)
        for as_of in dates:
            if as_of < window.test_start or as_of > window.test_end:
                continue
            next_idx = index[as_of] + 1
            if next_idx >= len(dates):
                continue
            weights = strategy.weights(data.up_to(as_of), as_of)
            if not weights:
                continue
            next_date = dates[next_idx]
            gross_returns.append(
                sum(
                    weight * (data.value(next_date, asset, return_field) or 0.0)
                    for asset, weight in weights.items()
                )
            )
            turnovers.append(_turnover(prev_weights, weights))
            return_dates.append(next_date)
            long_counts.append(sum(1 for w in weights.values() if w > 0))
            short_counts.append(sum(1 for w in weights.values() if w < 0))
            max_weights.append(max(abs(w) for w in weights.values()))
            prev_weights = weights

    net_returns = apply_linear_costs(gross_returns, turnovers, cost_bps)
    return WalkForwardResult(
        gross_returns=gross_returns,
        net_returns=net_returns,
        turnovers=turnovers,
        windows=tuple(windows),
        return_dates=return_dates,
        long_counts=long_counts,
        short_counts=short_counts,
        max_weights=max_weights,
    )


# The metric keys evaluate_walk_forward produces — also the coverage schema
# the metric-synthesis skill checks paper claims against before the bench runs.
WALK_FORWARD_METRIC_KEYS = (
    "mean_return", "volatility", "sharpe", "annualized_return", "max_drawdown",
    "calmar_ratio", "sortino_ratio", "expected_shortfall", "directional_accuracy",
    "profit_factor", "tail_ratio", "gross_mean_return", "average_turnover",
    "gross_pnl", "net_pnl",
    "avg_positions", "avg_long_positions", "avg_short_positions",
    "position_concentration",
)
_EMPTY_METRICS = WALK_FORWARD_METRIC_KEYS


def evaluate_walk_forward(
    result: WalkForwardResult, frequency: str
) -> dict[str, float]:
    """Frequency-aware metrics on the net OOS series, plus turnover/PnL/positions.

    Net-of-cost metrics come from the net series; ``gross_pnl``/``net_pnl``
    are cumulative simple PnL of the unit-notional book; position stats
    summarize the realized weight vectors.
    """

    if not result.net_returns:
        return {name: 0.0 for name in _EMPTY_METRICS}
    metrics = evaluate_series(result.net_returns, frequency)
    metrics["gross_mean_return"] = sum(result.gross_returns) / len(result.gross_returns)
    metrics["average_turnover"] = result.average_turnover
    metrics["gross_pnl"] = total_pnl(result.gross_returns)
    metrics["net_pnl"] = total_pnl(result.net_returns)
    metrics.update(result.position_distribution())
    return metrics


def _turnover(previous: dict[str, float], current: dict[str, float]) -> float:
    assets = set(previous) | set(current)
    return sum(abs(current.get(asset, 0.0) - previous.get(asset, 0.0)) for asset in assets)
