"""Synthetic worlds for validating the harness on known ground truth.

Principle 4 of the design note: run the machine on planted effects and on
pure noise before trusting it on real papers. If momentum cannot beat a
random null on the planted world, or *does* beat it on the noise world, the
harness is broken and nothing downstream is trustworthy.

Both generators are deterministic given a seed and produce monthly
``PanelData`` over a single ``return`` field.
"""

from __future__ import annotations

import random
from datetime import date

from quantbench_crew.benchmarks.contract import PanelData

DEFAULT_N_ASSETS = 20
DEFAULT_N_PERIODS = 180


def _monthly_dates(n_periods: int, start_year: int = 1965) -> list[date]:
    dates = []
    year, month = start_year, 1
    for _ in range(n_periods):
        dates.append(date(year, month, 28))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return dates


def planted_momentum(
    n_assets: int = DEFAULT_N_ASSETS,
    n_periods: int = DEFAULT_N_PERIODS,
    seed: int = 0,
    strength: float = 0.010,
    noise: float = 0.001,
) -> PanelData:
    """Persistent cross-sectional drift: past winners keep winning.

    Asset i carries a fixed drift spread linearly across ``[-strength,
    +strength]``; a long-short portfolio of the top vs bottom fraction earns
    roughly ``1.4 * strength`` per period before noise. Momentum ranking on
    past returns recovers that spread when noise is small relative to it.
    """

    rng = random.Random(seed)
    dates = _monthly_dates(n_periods)
    half = (n_assets - 1) / 2.0
    drifts = {
        f"A{i:02d}": strength * ((i - half) / half if half else 0.0)
        for i in range(n_assets)
    }
    records = []
    for d in dates:
        for asset, drift in drifts.items():
            records.append((d, asset, {"return": drift + rng.gauss(0.0, noise)}))
    return PanelData.from_records(records)


def pure_noise(
    n_assets: int = DEFAULT_N_ASSETS,
    n_periods: int = DEFAULT_N_PERIODS,
    seed: int = 0,
    noise: float = 0.02,
) -> PanelData:
    """Zero-mean iid returns: no cross-sectional signal exists to find."""

    rng = random.Random(seed)
    dates = _monthly_dates(n_periods)
    records = []
    for d in dates:
        for i in range(n_assets):
            records.append((d, f"A{i:02d}", {"return": rng.gauss(0.0, noise)}))
    return PanelData.from_records(records)
