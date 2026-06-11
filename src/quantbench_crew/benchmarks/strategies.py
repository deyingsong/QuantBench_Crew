"""Named strategy registry so the bench is not momentum-locked.

The evaluation set spans several anomaly families, so the walk-forward skill
selects a strategy by name. ``momentum`` is the Phase 1 reference; ``size``
is a market-cap sort; ``ml`` is a GKX-*style* cross-sectional predictor — the
simplest GKX model (a linear regression of next-period returns on firm
characteristics), implemented in pure Python via the project's own OLS so it
needs neither sklearn nor the numeric tier. Richer ML models (random forest,
gradient boosting) are a later extension behind the numeric seam.

Every strategy satisfies the Strategy contract and is point-in-time: ``fit``
sees only data up to ``train_end`` and ``weights`` only data up to ``as_of``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from quantbench_crew.benchmarks import reference_momentum
from quantbench_crew.benchmarks.spanning import ols


def _long_short(scores: dict[str, float], fraction: float) -> dict[str, float]:
    """Equal-weighted long-short book of the top/bottom ``fraction``."""

    if not scores:
        return {}
    ranked = sorted(scores, key=lambda asset: (scores[asset], asset))
    count = max(1, int(len(ranked) * fraction))
    weight = 1.0 / count
    book: dict[str, float] = {}
    for asset in ranked[-count:]:
        book[asset] = book.get(asset, 0.0) + weight
    for asset in ranked[:count]:
        book[asset] = book.get(asset, 0.0) - weight
    return book


class SizeStrategy:
    """Long small-cap, short large-cap — the size premium."""

    def __init__(self, params: Mapping[str, Any] | None = None) -> None:
        params = params or {}
        self.fraction = float(params.get("fraction", 0.3))
        self.cap_field = str(params.get("cap_field", "cap"))

    def fit(self, data, train_end):
        pass

    def weights(self, data, as_of):
        view = data.up_to(as_of)
        # Small cap = attractive, so negate so the top of the rank is smallest.
        scores = {
            asset: -value
            for asset in view.assets()
            if (value := view.value(as_of, asset, self.cap_field)) is not None
        }
        return _long_short(scores, self.fraction)


class MLCrossSectionStrategy:
    """GKX-style linear cross-sectional return predictor (pure-Python OLS).

    Fits next-period returns on standardized firm characteristics over the
    training window, then longs the highest-predicted and shorts the
    lowest-predicted names. Standardization uses train-window moments only, so
    there is no look-ahead in the feature scaling.
    """

    def __init__(self, params: Mapping[str, Any] | None = None) -> None:
        params = params or {}
        self.features = tuple(params.get("features", ("cap", "std_ret", "max_ret")))
        self.fraction = float(params.get("fraction", 0.3))
        self.field = str(params.get("field", "return"))
        self._beta: list[float] | None = None
        self._mean: list[float] = []
        self._std: list[float] = []

    def fit(self, data, train_end):
        view = data.up_to(train_end)
        dates = view.dates()
        feature_rows: list[list[float]] = []
        targets: list[float] = []
        for i, day in enumerate(dates[:-1]):
            next_day = dates[i + 1]
            for asset in view.assets():
                feats = [view.value(day, asset, f) for f in self.features]
                target = view.value(next_day, asset, self.field)
                if target is None or any(f is None for f in feats):
                    continue
                feature_rows.append([float(f) for f in feats])
                targets.append(float(target))

        if len(feature_rows) <= len(self.features) + 1:
            self._beta = None
            return

        k = len(self.features)
        self._mean = [sum(r[j] for r in feature_rows) / len(feature_rows) for j in range(k)]
        self._std = []
        for j in range(k):
            var = sum((r[j] - self._mean[j]) ** 2 for r in feature_rows) / len(feature_rows)
            self._std.append(var ** 0.5 or 1.0)

        design = [[1.0, *self._standardize(r)] for r in feature_rows]
        try:
            self._beta = ols(targets, design)["beta"]
        except ValueError:  # singular design (collinear characteristics)
            self._beta = None

    def weights(self, data, as_of):
        if self._beta is None:
            return {}
        view = data.up_to(as_of)
        predictions: dict[str, float] = {}
        for asset in view.assets():
            feats = [view.value(as_of, asset, f) for f in self.features]
            if any(f is None for f in feats):
                continue
            row = [1.0, *self._standardize([float(f) for f in feats])]
            predictions[asset] = sum(b * x for b, x in zip(self._beta, row))
        return _long_short(predictions, self.fraction)

    def _standardize(self, row: list[float]) -> list[float]:
        return [(value - m) / s for value, m, s in zip(row, self._mean, self._std)]


_BUILDERS = {
    "momentum": lambda params: reference_momentum.build_strategy(params),
    "size": lambda params: SizeStrategy(params),
    "ml": lambda params: MLCrossSectionStrategy(params),
}


def build_named_strategy(name: str, params: Mapping[str, Any] | None = None):
    """Construct a strategy by registry name."""

    try:
        return _BUILDERS[name](params)
    except KeyError:
        raise ValueError(
            f"unknown strategy {name!r}; expected one of {sorted(_BUILDERS)}"
        ) from None


def strategy_purge(name: str, params: Mapping[str, Any]) -> int:
    """Walk-forward purge for a strategy (momentum needs its formation window)."""

    if name == "momentum":
        return int(params.get("formation_periods", 6)) + int(params.get("skip_periods", 1))
    return 1
