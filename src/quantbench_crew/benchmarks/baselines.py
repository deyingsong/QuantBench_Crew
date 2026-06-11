"""Baseline strategies, including the random-matched-turnover null.

The random-matched-turnover baseline is the significance floor: it takes the
same long/short position sizing as the candidate but selects assets at
random, so it pays the same turnover cost while carrying no signal. A
candidate that does not beat this null is not distinguishable from luck
(Lopez de Prado's reframing of the multiple-testing problem). Equal-weight
and buy-and-hold give long-only references.
"""

from __future__ import annotations

import random
from datetime import date

from quantbench_crew.benchmarks.contract import PanelData


def _assets_with_history(data: PanelData, as_of: date, field: str, periods: int) -> list[str]:
    return [
        asset
        for asset in data.assets()
        if len(data.history(asset, field, end=as_of, periods=periods)) >= periods
    ]


class EqualWeightStrategy:
    """Long-only, equal weight across assets with enough history."""

    def __init__(self, params=None):
        params = params or {}
        self.field = str(params.get("field", "return"))
        self.min_history = int(params.get("min_history", 1))

    def fit(self, data, train_end):
        pass

    def weights(self, data, as_of):
        view = data.up_to(as_of)
        assets = _assets_with_history(view, as_of, self.field, self.min_history)
        if not assets:
            return {}
        weight = 1.0 / len(assets)
        return {asset: weight for asset in assets}


class BuyAndHoldStrategy:
    """Equal weight fixed at the first fit; held constant thereafter."""

    def __init__(self, params=None):
        params = params or {}
        self.field = str(params.get("field", "return"))
        self._held: dict[str, float] = {}

    def fit(self, data, train_end):
        view = data.up_to(train_end)
        assets = view.assets()
        if assets:
            weight = 1.0 / len(assets)
            self._held = {asset: weight for asset in assets}

    def weights(self, data, as_of):
        return dict(self._held)


class RandomMatchedTurnoverStrategy:
    """Random long-short with the candidate's sizing — the significance floor.

    Same formation-window gate and same long/short counts as cross-sectional
    momentum, but ranks on a seeded random key instead of past returns. Its
    turnover therefore tracks the momentum strategy's, isolating signal from
    trading cost.
    """

    def __init__(self, params=None):
        params = params or {}
        self.formation = int(params.get("formation_periods", 6))
        self.skip = int(params.get("skip_periods", 1))
        self.fraction = float(params.get("fraction", 0.3))
        self.field = str(params.get("field", "return"))
        self.seed = int(params.get("seed", 0))

    def fit(self, data, train_end):
        pass

    def weights(self, data, as_of):
        view = data.up_to(as_of)
        eligible = _assets_with_history(
            view, as_of, self.field, self.formation + self.skip
        )
        if not eligible:
            return {}
        # Seed per-date so selection is deterministic but varies over time,
        # producing churn comparable to the momentum strategy's. (Random only
        # accepts scalar seeds, so fold the date into an int.)
        rng = random.Random(self.seed * 1_000_003 + as_of.toordinal())
        ranked = sorted(eligible, key=lambda asset: (rng.random(), asset))
        count = max(1, int(len(ranked) * self.fraction))
        weight = 1.0 / count
        result: dict[str, float] = {}
        for asset in ranked[-count:]:
            result[asset] = result.get(asset, 0.0) + weight
        for asset in ranked[:count]:
            result[asset] = result.get(asset, 0.0) - weight
        return result


def build_baselines(params=None):
    """Construct the standard baseline suite keyed by name."""

    params = params or {}
    return {
        "equal_weight": EqualWeightStrategy(params),
        "buy_and_hold": BuyAndHoldStrategy(params),
        "random_matched_turnover": RandomMatchedTurnoverStrategy(params),
    }
