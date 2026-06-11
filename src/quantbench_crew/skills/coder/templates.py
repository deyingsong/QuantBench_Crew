"""Deterministic test templates for candidate strategies (QB-09 P0).

``compose_test_script`` appends a self-contained harness to a candidate
module's source: the result is one sandbox-runnable script that checks the
three template properties and prints a single JSON line with the outcome.

The three checks are the anti-Goodhart floor every candidate must clear
before any benchmark metric is computed:

- shape: ``build_strategy(params)`` yields an object whose ``weights`` is a
  non-empty dict of finite floats keyed by known assets;
- determinism: two fresh instances on identical inputs produce identical
  weights;
- no-lookahead: weights at t are unchanged when data strictly after t is
  perturbed — the candidate gets the *full* mutated panel, so passing
  requires point-in-time discipline inside the strategy.

Templates are parameterized by MethodSpec fields (formation/holding horizons
size the synthetic panel and the params handed to ``build_strategy``). The
harness must stay admissible to the sandbox AST gate: stdlib-only imports,
no dunder access, no banned calls.
"""

from __future__ import annotations

import json
from typing import Any

from quantbench_crew.models import MethodSpec

TEMPLATE_TEST_COUNT = 3

_HARNESS = '''

# === deterministic template test harness (generated) ===
import json as _json
import random as _random
from datetime import date as _date, timedelta as _timedelta


class _Panel:
    """Minimal PanelData duck type for sandboxed checks."""

    def __init__(self, frames, all_dates):
        self._frames = frames
        self._dates = tuple(sorted(all_dates))

    def dates(self):
        return self._dates

    def assets(self):
        names = set()
        for frame in self._frames.values():
            names.update(frame)
        return tuple(sorted(names))

    def value(self, as_of, asset, field, default=None):
        return self._frames.get(as_of, {}).get(asset, {}).get(field, default)

    def history(self, asset, field, end, periods):
        values = [
            self._frames[d][asset][field]
            for d in self._dates
            if d <= end and field in self._frames.get(d, {}).get(asset, {})
        ]
        return tuple(values[-periods:])

    def up_to(self, as_of):
        kept = {d: frame for d, frame in self._frames.items() if d <= as_of}
        return _Panel(kept, kept.keys())


def _make_panel(periods, n_assets, seed, mutate_after=None):
    rng = _random.Random(seed)
    start = _date(2020, 1, 1)
    all_dates = [start + _timedelta(days=30 * i) for i in range(periods)]
    frames = {}
    for d in all_dates:
        frame = {}
        for j in range(n_assets):
            drift = 0.01 * (j - (n_assets - 1) / 2.0) / max(1, n_assets - 1)
            r = drift + rng.gauss(0.0, 0.02)
            if mutate_after is not None and d > mutate_after:
                r = r * 3.0 + 0.05
            frame["A" + str(j).zfill(2)] = {"return": r}
        frames[d] = frame
    return _Panel(frames, all_dates)


def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return value == value and value not in (float("inf"), float("-inf"))


def _run_template_checks():
    periods = __PERIODS__
    n_assets = __N_ASSETS__
    params = _json.loads('__PARAMS_JSON__')
    failures = []

    panel = _make_panel(periods, n_assets, seed=7)
    as_of = panel.dates()[-3]

    # shape
    weights = None
    try:
        strategy = build_strategy(dict(params))
        strategy.fit(panel.up_to(as_of), as_of)
        weights = strategy.weights(panel.up_to(as_of), as_of)
        if not isinstance(weights, dict) or not weights:
            failures.append("shape: weights must be a non-empty dict")
        else:
            known = set(panel.assets())
            for key, value in weights.items():
                if key not in known:
                    failures.append("shape: unknown asset " + repr(key))
                    break
                if not _finite_number(value):
                    failures.append("shape: non-finite weight for " + repr(key))
                    break
    except Exception as exc:
        failures.append("shape: raised " + repr(exc))

    if weights is None or any(f.startswith("shape:") for f in failures):
        print(_json.dumps({"passed": 0, "total": __TOTAL__, "failures": failures}))
        return

    # determinism
    try:
        again = build_strategy(dict(params))
        again.fit(panel.up_to(as_of), as_of)
        if again.weights(panel.up_to(as_of), as_of) != weights:
            failures.append("determinism: weights differ across identical runs")
    except Exception as exc:
        failures.append("determinism: raised " + repr(exc))

    # no-lookahead: hand the FULL mutated panel to the candidate
    try:
        mutated = _make_panel(periods, n_assets, seed=7, mutate_after=as_of)
        candidate = build_strategy(dict(params))
        candidate.fit(mutated.up_to(as_of), as_of)
        if candidate.weights(mutated, as_of) != weights:
            failures.append(
                "no_lookahead: weights at t change when post-t data changes"
            )
    except Exception as exc:
        failures.append("no_lookahead: raised " + repr(exc))

    # spec-derived construction invariants (QB-29): each from a trusted
    # vocabulary, applied to the already-computed weights.
    nonzero = [v for v in weights.values() if abs(v) > 1e-12]
    for invariant in _json.loads('__INVARIANTS_JSON__'):
        kind = invariant["kind"]
        try:
            if kind == "zero_net":
                if abs(sum(weights.values())) > 1e-6:
                    failures.append("zero_net: long-short weights do not sum to ~0")
            elif kind == "uniform_magnitude":
                mags = sorted(abs(v) for v in nonzero)
                if mags and (mags[-1] - mags[0]) > 1e-6:
                    failures.append("uniform_magnitude: equal-weight legs are not uniform")
            elif kind == "leveraged_bound":
                if sum(abs(v) for v in weights.values()) > 2.0 + 1e-6:
                    failures.append("leveraged_bound: gross exposure exceeds 2x")
        except Exception as exc:
            failures.append(kind + ": raised " + repr(exc))

    failed_checks = {failure.split(":")[0] for failure in failures}
    print(
        _json.dumps(
            {
                "passed": __TOTAL__ - len(failed_checks),
                "total": __TOTAL__,
                "failures": failures,
            }
        )
    )


_run_template_checks()
'''


def template_params(spec: MethodSpec | None) -> dict[str, Any]:
    """Strategy params derived from MethodSpec hyperparameters."""

    hyperparameters = spec.hyperparameters if spec is not None else {}
    return {
        "formation_periods": int(hyperparameters.get("formation_months", 6)),
        "skip_periods": 1,
        "fraction": 0.3,
        "field": "return",
    }


_LONG_SHORT_MARKERS = (
    "long-short", "long short", "winner-minus-loser", "winners-minus-losers", "wml",
)
_EQUAL_WEIGHT_MARKERS = ("equal-weight", "equal weight", "equally weighted", "equally-weighted")


def spec_invariants(spec: MethodSpec | None) -> list[dict[str, Any]]:
    """Construction-aware invariants implied by the MethodSpec (QB-29).

    Derived from a trusted vocabulary rather than emitted as code, so nothing
    untrusted enters the harness: the LLM (or the deterministic parser) only
    selects *which* known invariants apply, never writes the assertion.
    """

    if spec is None:
        return []
    text = (spec.portfolio_construction or "").lower()
    invariants: list[dict[str, Any]] = []
    if any(marker in text for marker in _LONG_SHORT_MARKERS):
        invariants.append({"kind": "zero_net"})
    if any(marker in text for marker in _EQUAL_WEIGHT_MARKERS):
        invariants.append({"kind": "uniform_magnitude"})
    invariants.append({"kind": "leveraged_bound"})  # always: sanity cap on gross exposure
    return invariants


def template_test_count(spec: MethodSpec | None) -> int:
    """Total checks the harness runs for this spec (templates + invariants)."""

    return TEMPLATE_TEST_COUNT + len(spec_invariants(spec))


def compose_test_script(candidate_source: str, spec: MethodSpec | None) -> str:
    """One sandbox-runnable script: candidate module + template harness."""

    params = template_params(spec)
    invariants = spec_invariants(spec)
    # Enough history for formation + skip plus a comfortable margin.
    periods = max(24, 2 * (params["formation_periods"] + params["skip_periods"]) + 6)
    harness = (
        _HARNESS.replace("__PERIODS__", str(periods))
        .replace("__N_ASSETS__", "10")
        .replace("__PARAMS_JSON__", json.dumps(params))
        .replace("__INVARIANTS_JSON__", json.dumps(invariants))
        .replace("__TOTAL__", str(TEMPLATE_TEST_COUNT + len(invariants)))
    )
    return candidate_source.rstrip() + "\n" + harness


def parse_template_result(stdout: str) -> dict[str, Any] | None:
    """Parse the harness's JSON line from sandbox stdout."""

    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "passed" in payload and "total" in payload:
            return payload
    return None
