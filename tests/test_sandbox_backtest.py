"""QB-32: generated strategies run through the bench via the sandbox."""

from quantbench_crew.benchmarks.protocols import run_walk_forward, walk_forward_windows
from quantbench_crew.benchmarks.reference_momentum import build_strategy
from quantbench_crew.benchmarks.sandbox_backtest import sandbox_backtest
from quantbench_crew.datasets import synthetic
from quantbench_crew.skills.coder.code_generation import reference_source

PARAMS = {"formation_periods": 6, "skip_periods": 1, "fraction": 0.3, "field": "return"}

IMPORT_CHEATER = '''
import os
def build_strategy(params=None):
    return None
'''


def _setup(seed: int = 0):
    panel = synthetic.planted_momentum(seed=seed, n_periods=72)
    windows = walk_forward_windows(panel.dates(), 24, 12, purge=7, embargo=1)
    return panel, windows


def test_sandboxed_backtest_matches_host_side_within_tolerance() -> None:
    panel, windows = _setup()
    # The reference module stands in for a "generated" candidate: run it in the
    # sandbox and confirm the OOS returns match the trusted host-side harness.
    host = run_walk_forward(build_strategy(PARAMS), panel, windows, cost_bps=10.0)
    sandboxed = sandbox_backtest(reference_source(), panel, windows, PARAMS, cost_bps=10.0)

    assert sandboxed["status"] == "ok"
    assert len(sandboxed["returns"]) == len(host.net_returns) > 0
    for got, want in zip(sandboxed["returns"], host.net_returns):
        assert abs(got - want) < 1e-9
    assert sandboxed["return_dates"] == host.return_dates


def test_sandboxed_backtest_blocks_forbidden_import() -> None:
    panel, windows = _setup()
    result = sandbox_backtest(IMPORT_CHEATER, panel, windows, PARAMS)

    assert result["status"] == "blocked"
    assert result["returns"] == []
    assert any("os" in v for v in result["violations"])


def test_sandboxed_backtest_reports_runtime_errors() -> None:
    panel, windows = _setup()
    broken = "def build_strategy(params=None):\n    raise RuntimeError('boom')\n"
    result = sandbox_backtest(broken, panel, windows, PARAMS)

    assert result["status"] in ("error", "timeout")
    assert result["returns"] == []
