"""Benchmark contracts, reference strategies, and evaluation runners."""

from quantbench_crew.benchmarks.backtest import run_backtest
from quantbench_crew.benchmarks.contract import PanelData, Strategy
from quantbench_crew.benchmarks.reference_momentum import MomentumStrategy, build_strategy

DEFAULT_SAMPLE_RETURNS = [0.01, -0.004, 0.006, 0.0, 0.012, -0.008, 0.004]

__all__ = [
    "DEFAULT_SAMPLE_RETURNS",
    "MomentumStrategy",
    "PanelData",
    "Strategy",
    "build_strategy",
    "run_backtest",
]
