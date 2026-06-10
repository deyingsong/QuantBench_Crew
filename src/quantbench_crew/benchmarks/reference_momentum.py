"""Reference cross-sectional momentum strategy.

Hand-written de-risking implementation for the Strategy contract, and the
deterministic fallback template for code generation: this module is
deliberately self-contained (stdlib-only, no quantbench imports at runtime),
so its source can be emitted verbatim as a sandbox candidate and run against
the PanelData duck API. Keep it that way — anything imported here that does
not exist inside the sandbox breaks the fallback generator.

Signal: rank assets on cumulative returns over the formation window, skipping
the most recent ``skip_periods`` (the classic reversal guard). Portfolio:
equal-weighted long the top fraction, short the bottom fraction, zero net.
"""

from __future__ import annotations

DEFAULT_PARAMS = {
    "formation_periods": 6,
    "skip_periods": 1,
    "fraction": 0.3,
    "field": "return",
}


class MomentumStrategy:
    """Cross-sectional momentum over a point-in-time panel."""

    def __init__(self, params=None):
        merged = dict(DEFAULT_PARAMS)
        merged.update(params or {})
        self.params = merged

    def fit(self, data, train_end):
        # Momentum has no estimated parameters; recorded for protocol parity.
        self._fitted_through = train_end

    def weights(self, data, as_of):
        formation = int(self.params["formation_periods"])
        skip = int(self.params["skip_periods"])
        fraction = float(self.params["fraction"])
        field = str(self.params["field"])

        view = data.up_to(as_of)  # no-lookahead even if callers pass full data
        scores = {}
        for asset in view.assets():
            history = view.history(asset, field, end=as_of, periods=formation + skip)
            if len(history) < formation + skip:
                continue
            window = history[: len(history) - skip] if skip else history
            cumulative = 1.0
            for period_return in window[-formation:]:
                cumulative *= 1.0 + period_return
            scores[asset] = cumulative - 1.0

        if not scores:
            return {}

        ranked = sorted(scores, key=lambda asset: (scores[asset], asset))
        count = max(1, int(len(ranked) * fraction))
        weight = 1.0 / count
        result = {}
        for asset in ranked[-count:]:
            result[asset] = result.get(asset, 0.0) + weight
        for asset in ranked[:count]:
            result[asset] = result.get(asset, 0.0) - weight
        return result


def build_strategy(params=None):
    """Entry point required of every generated strategy module."""

    return MomentumStrategy(params)
