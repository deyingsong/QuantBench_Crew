"""Minimal backtest loop: Strategy + PanelData -> portfolio returns.

This is the simple end-to-end runner QB-09 needs; the walk-forward protocol
with purged/embargoed splits and refit schedules replaces it for evaluation
in QB-13. Weights are formed at t on data up to t and applied to returns at
t+1, so the loop itself cannot leak.
"""

from __future__ import annotations

from quantbench_crew.benchmarks.contract import PanelData, Strategy


def run_backtest(
    strategy: Strategy, data: PanelData, return_field: str = "return"
) -> list[float]:
    """Return the strategy's per-period portfolio returns over the panel."""

    dates = data.dates()
    if len(dates) < 2:
        return []

    strategy.fit(data.up_to(dates[0]), dates[0])

    portfolio_returns: list[float] = []
    for index, as_of in enumerate(dates[:-1]):
        weights = strategy.weights(data.up_to(as_of), as_of)
        if not weights:
            continue  # warmup: not enough history to form a portfolio
        next_date = dates[index + 1]
        portfolio_returns.append(
            sum(
                weight * (data.value(next_date, asset, return_field) or 0.0)
                for asset, weight in weights.items()
            )
        )
    return portfolio_returns
