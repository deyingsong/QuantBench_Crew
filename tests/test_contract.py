"""QB-09 acceptance: contract, reference momentum, and bench-harness flow."""

import random
from datetime import date, timedelta

import pytest

from quantbench_crew.agents.bench import QuantBenchAgent
from quantbench_crew.benchmarks import (
    MomentumStrategy,
    PanelData,
    Strategy,
    build_strategy,
    run_backtest,
)
from quantbench_crew.models import ImplementationPlan, Paper


def _panel(asset_returns: dict[str, list[float]]) -> PanelData:
    start = date(2020, 1, 1)
    records = []
    for asset, returns in asset_returns.items():
        for index, value in enumerate(returns):
            records.append((start + timedelta(days=30 * index), asset, {"return": value}))
    return PanelData.from_records(records)


def test_panel_data_access_and_point_in_time() -> None:
    panel = _panel({"A": [0.01, 0.02, 0.03], "B": [-0.01, -0.02, -0.03]})
    dates = panel.dates()

    assert len(dates) == 3 and dates == tuple(sorted(dates))
    assert panel.assets() == ("A", "B")
    assert panel.value(dates[1], "A", "return") == pytest.approx(0.02)
    assert panel.value(dates[1], "A", "missing", default=0.0) == 0.0
    assert panel.history("A", "return", end=dates[1], periods=5) == (0.01, 0.02)

    truncated = panel.up_to(dates[1])
    assert truncated.dates() == dates[:2]
    assert truncated.value(dates[2], "A", "return") is None


def test_momentum_strategy_longs_winners_shorts_losers() -> None:
    panel = _panel(
        {
            "WIN": [0.02] * 8,
            "LOSE": [-0.02] * 8,
            "FLAT": [0.0] * 8,
        }
    )
    strategy = build_strategy({"formation_periods": 3, "skip_periods": 1, "fraction": 0.34})
    as_of = panel.dates()[-2]

    weights = strategy.weights(panel, as_of)

    assert weights["WIN"] == pytest.approx(1.0)
    assert weights["LOSE"] == pytest.approx(-1.0)
    assert "FLAT" not in weights
    assert sum(weights.values()) == pytest.approx(0.0)


def test_momentum_satisfies_strategy_protocol_and_determinism() -> None:
    panel = _panel({f"A{i}": [0.01 * (i - 2)] * 10 for i in range(5)})
    as_of = panel.dates()[-1]

    assert isinstance(MomentumStrategy(), Strategy)

    first = build_strategy()
    second = build_strategy()
    first.fit(panel.up_to(as_of), as_of)
    second.fit(panel.up_to(as_of), as_of)
    assert first.weights(panel, as_of) == second.weights(panel, as_of)


def test_momentum_has_no_lookahead() -> None:
    rng = random.Random(11)
    panel = _panel({f"A{i}": [rng.gauss(0.0, 0.02) for _ in range(12)] for i in range(6)})
    as_of = panel.dates()[6]
    strategy = build_strategy({"formation_periods": 3})

    from_full = strategy.weights(panel, as_of)
    from_truncated = strategy.weights(panel.up_to(as_of), as_of)

    assert from_full == from_truncated and from_full


def test_warmup_periods_produce_no_weights() -> None:
    panel = _panel({"A": [0.01, 0.01], "B": [-0.01, -0.01]})
    strategy = build_strategy({"formation_periods": 6, "skip_periods": 1})

    assert strategy.weights(panel, panel.dates()[-1]) == {}


def test_reference_momentum_runs_through_bench_harness_end_to_end() -> None:
    # Planted persistent cross-sectional dispersion: past winners stay
    # winners, so momentum must earn positive average returns here.
    rng = random.Random(0)
    panel = _panel(
        {
            f"A{i:02d}": [0.002 * (i - 4.5) + rng.gauss(0.0, 0.001) for _ in range(30)]
            for i in range(10)
        }
    )
    strategy = build_strategy({"formation_periods": 6, "skip_periods": 1, "fraction": 0.3})

    portfolio_returns = run_backtest(strategy, panel)

    assert len(portfolio_returns) > 10
    assert sum(portfolio_returns) / len(portfolio_returns) > 0

    paper = Paper(title="Reference Momentum", abstract="planted world")
    plan = ImplementationPlan(
        paper=paper, modules=("m",), assumptions=(), tests=(), open_questions=()
    )
    result = QuantBenchAgent().evaluate(plan, returns=portfolio_returns, dataset="planted")

    assert result.dataset == "planted"
    assert result.metrics["sharpe"] > 0
    assert "mean_return" in result.metrics
