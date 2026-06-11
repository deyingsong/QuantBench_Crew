"""Benchmark contracts, reference strategies, and evaluation runners."""

from quantbench_crew.benchmarks.backtest import run_backtest
from quantbench_crew.benchmarks.baselines import build_baselines
from quantbench_crew.benchmarks.claims import compare_claims
from quantbench_crew.benchmarks.contract import PanelData, Strategy
from quantbench_crew.benchmarks.metrics import evaluate_series, periods_per_year
from quantbench_crew.benchmarks.protocols import (
    WalkForwardResult,
    WalkForwardWindow,
    evaluate_walk_forward,
    run_walk_forward,
    walk_forward_windows,
)
from quantbench_crew.benchmarks.reference_momentum import MomentumStrategy, build_strategy

DEFAULT_SAMPLE_RETURNS = [0.01, -0.004, 0.006, 0.0, 0.012, -0.008, 0.004]

__all__ = [
    "DEFAULT_SAMPLE_RETURNS",
    "MomentumStrategy",
    "PanelData",
    "Strategy",
    "WalkForwardResult",
    "WalkForwardWindow",
    "build_baselines",
    "build_strategy",
    "compare_claims",
    "evaluate_series",
    "evaluate_walk_forward",
    "periods_per_year",
    "run_backtest",
    "run_walk_forward",
    "walk_forward_windows",
]
