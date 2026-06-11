"""Robustness interpretation: subsample stability and parameter sensitivity.

A real effect persists when you cut the sample in half and when you nudge the
parameters; an overfit one does not. Subsample stability splits the realized
out-of-sample series and checks the Sharpe keeps its sign; parameter
sensitivity sweeps the strategy's key knob and reports the Sharpe spread. The
reviewer reads the resulting ``RobustnessReport`` to separate a durable
result from a fragile one.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from quantbench_crew.benchmarks.contract import PanelData, Strategy
from quantbench_crew.benchmarks.metrics import annualized_sharpe
from quantbench_crew.benchmarks.protocols import (
    WalkForwardResult,
    WalkForwardWindow,
    evaluate_walk_forward,
    run_walk_forward,
)
from quantbench_crew.models import RobustnessReport

StrategyFactory = Callable[[Mapping[str, Any]], Strategy]
DEFAULT_SWEEP = (3, 6, 9, 12)


def subsample_sharpes(
    result: WalkForwardResult, frequency: str, n_splits: int = 2
) -> dict[str, float]:
    """Annualized Sharpe within each contiguous split of the OOS series."""

    returns = result.net_returns
    dates = result.return_dates
    if len(returns) < n_splits * 2:
        return {}

    out: dict[str, float] = {}
    size = len(returns) // n_splits
    for split in range(n_splits):
        lo = split * size
        hi = len(returns) if split == n_splits - 1 else (split + 1) * size
        label = f"{dates[lo].isoformat()}..{dates[hi - 1].isoformat()}" if dates else f"split_{split}"
        out[label] = annualized_sharpe(returns[lo:hi], frequency)
    return out


def parameter_sensitivity(
    build: StrategyFactory,
    data: PanelData,
    windows: list[WalkForwardWindow],
    base_params: Mapping[str, Any],
    frequency: str,
    *,
    sweep_param: str = "formation_periods",
    sweep_values: Sequence[int] = DEFAULT_SWEEP,
    cost_bps: float = 10.0,
) -> dict[str, float]:
    """Sharpe at each value of ``sweep_param`` (label -> sharpe, plus spread)."""

    sharpes: dict[str, float] = {}
    for value in sweep_values:
        params = {**base_params, sweep_param: value}
        result = run_walk_forward(build(params), data, windows, cost_bps=cost_bps)
        sharpes[f"{sweep_param}={value}"] = evaluate_walk_forward(result, frequency)["sharpe"]
    if sharpes:
        sharpes["spread"] = max(sharpes.values()) - min(sharpes.values())
    return sharpes


def build_robustness_report(
    build: StrategyFactory,
    data: PanelData,
    windows: list[WalkForwardWindow],
    base_params: Mapping[str, Any],
    frequency: str,
    *,
    sweep_param: str = "formation_periods",
    sweep_values: Sequence[int] = DEFAULT_SWEEP,
    cost_bps: float = 10.0,
) -> RobustnessReport:
    """Run the candidate, split it, sweep it, and judge sign stability."""

    full = run_walk_forward(build(base_params), data, windows, cost_bps=cost_bps)
    full_sharpe = evaluate_walk_forward(full, frequency)["sharpe"]
    subs = subsample_sharpes(full, frequency, n_splits=2)
    sensitivity = parameter_sensitivity(
        build, data, windows, base_params, frequency,
        sweep_param=sweep_param, sweep_values=sweep_values, cost_bps=cost_bps,
    )

    # Stable = positive overall and every subsample keeps that sign.
    sign_stable = bool(subs) and full_sharpe > 0 and all(s > 0 for s in subs.values())
    notes = (
        f"full-sample sharpe {full_sharpe:.2f}; "
        + ("sign-stable across subsamples" if sign_stable else "sign flips across subsamples"),
    )
    return RobustnessReport(
        subsample_sharpes=subs,
        sign_stable=sign_stable,
        parameter_sensitivity=sensitivity,
        notes=notes,
    )


def robustness_to_dict(r: RobustnessReport) -> dict:
    return {
        "subsample_sharpes": dict(r.subsample_sharpes),
        "sign_stable": r.sign_stable,
        "parameter_sensitivity": dict(r.parameter_sensitivity),
        "notes": list(r.notes),
    }


def robustness_from_dict(data: dict | None) -> RobustnessReport | None:
    if not data:
        return None
    return RobustnessReport(
        subsample_sharpes={k: float(v) for k, v in data["subsample_sharpes"].items()},
        sign_stable=bool(data["sign_stable"]),
        parameter_sensitivity={k: float(v) for k, v in data["parameter_sensitivity"].items()},
        notes=tuple(data.get("notes", ())),
    )
