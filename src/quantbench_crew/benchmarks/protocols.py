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

from dataclasses import dataclass
from datetime import date

from quantbench_crew.benchmarks.contract import PanelData, Strategy
from quantbench_crew.benchmarks.metrics import apply_linear_costs, evaluate_series


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

    @property
    def average_turnover(self) -> float:
        return sum(self.turnovers) / len(self.turnovers) if self.turnovers else 0.0


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
            prev_weights = weights

    net_returns = apply_linear_costs(gross_returns, turnovers, cost_bps)
    return WalkForwardResult(
        gross_returns=gross_returns,
        net_returns=net_returns,
        turnovers=turnovers,
        windows=tuple(windows),
    )


def evaluate_walk_forward(
    result: WalkForwardResult, frequency: str
) -> dict[str, float]:
    """Frequency-aware metrics on the net OOS series, plus turnover."""

    if not result.net_returns:
        return {
            "mean_return": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "annualized_return": 0.0,
            "max_drawdown": 0.0,
            "gross_mean_return": 0.0,
            "average_turnover": 0.0,
        }
    metrics = evaluate_series(result.net_returns, frequency)
    metrics["gross_mean_return"] = sum(result.gross_returns) / len(result.gross_returns)
    metrics["average_turnover"] = result.average_turnover
    return metrics


def _turnover(previous: dict[str, float], current: dict[str, float]) -> float:
    assets = set(previous) | set(current)
    return sum(abs(current.get(asset, 0.0) - previous.get(asset, 0.0)) for asset in assets)
