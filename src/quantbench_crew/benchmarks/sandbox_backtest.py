"""Run an untrusted generated strategy through a walk-forward in the sandbox.

QB-32 closes the Coder->Bench seam for *generated* code. A generated strategy
is untrusted, so it must never run host-side in :mod:`protocols`. Instead this
module composes a stdlib-only backtest harness around the candidate, embeds the
panel and the walk-forward windows **in memory** (no file or network access —
the data is a JSON literal the harness parses), runs it through
:func:`run_sandboxed`, and parses the realized out-of-sample returns from
stdout. The bench then computes metrics / deflated Sharpe from those returns
exactly as for the trusted path.

The harness mirrors :func:`run_walk_forward` arithmetic (weights at t applied
to t+1 return, two-sided turnover cost) using ISO-string dates so it needs no
non-stdlib imports — ISO dates sort and compare identically to ``date``.
"""

from __future__ import annotations

import json
from datetime import date

from quantbench_crew.benchmarks.contract import PanelData
from quantbench_crew.benchmarks.protocols import WalkForwardWindow
from quantbench_crew.tools.code_runner import DEFAULT_ALLOWED_IMPORTS, run_sandboxed

_HARNESS = '''

# === sandboxed walk-forward harness (generated) ===
import json as _json


class _Panel:
    def __init__(self, frames, all_dates):
        self._frames = frames
        self._dates = tuple(sorted(all_dates))

    @classmethod
    def from_records(cls, records):
        frames = {}
        for day, asset, fields in records:
            frames.setdefault(day, {}).setdefault(asset, {}).update(fields)
        return cls(frames, frames.keys())

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


def _run_backtest():
    panel = _Panel.from_records(_json.loads('__RECORDS__'))
    windows = _json.loads('__WINDOWS__')
    params = _json.loads('__PARAMS__')
    field = '__FIELD__'
    cost_rate = __COST_BPS__ / 10000.0

    dates = panel.dates()
    index = {d: i for i, d in enumerate(dates)}
    gross, turnovers, return_dates = [], [], []
    prev = {}

    for train_end, test_start, test_end in windows:
        strategy = build_strategy(dict(params))
        strategy.fit(panel.up_to(train_end), train_end)
        for as_of in dates:
            if as_of < test_start or as_of > test_end:
                continue
            nxt = index[as_of] + 1
            if nxt >= len(dates):
                continue
            weights = strategy.weights(panel.up_to(as_of), as_of)
            if not weights:
                continue
            next_date = dates[nxt]
            gross.append(sum(
                w * (panel.value(next_date, a, field) or 0.0) for a, w in weights.items()
            ))
            keys = set(weights) | set(prev)
            turnovers.append(sum(abs(weights.get(a, 0.0) - prev.get(a, 0.0)) for a in keys))
            return_dates.append(next_date)
            prev = weights

    net = [g - t * cost_rate for g, t in zip(gross, turnovers)]
    print(_json.dumps({"returns": net, "return_dates": return_dates}))


_run_backtest()
'''


def compose_backtest_script(
    candidate_source: str,
    panel: PanelData,
    windows: list[WalkForwardWindow],
    params: dict,
    return_field: str = "return",
    cost_bps: float = 10.0,
) -> str:
    """Candidate module + an in-memory walk-forward harness, sandbox-runnable."""

    records = [
        [d.isoformat(), asset, {k: v for k, v in fields}]
        for d, asset, fields in panel.records()
    ]
    window_rows = [
        [w.train_end.isoformat(), w.test_start.isoformat(), w.test_end.isoformat()]
        for w in windows
    ]
    harness = (
        _HARNESS.replace("__RECORDS__", json.dumps(records))
        .replace("__WINDOWS__", json.dumps(window_rows))
        .replace("__PARAMS__", json.dumps(params))
        .replace("__FIELD__", return_field)
        .replace("__COST_BPS__", repr(float(cost_bps)))
    )
    return candidate_source.rstrip() + "\n" + harness


def parse_backtest_result(stdout: str) -> dict | None:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "returns" in payload:
            return payload
    return None


def sandbox_backtest(
    candidate_source: str,
    panel: PanelData,
    windows: list[WalkForwardWindow],
    params: dict,
    *,
    return_field: str = "return",
    cost_bps: float = 10.0,
    allowed_imports=DEFAULT_ALLOWED_IMPORTS,
    timeout: float = 30.0,
) -> dict:
    """Backtest an untrusted candidate; returns status + net OOS returns/dates."""

    script = compose_backtest_script(
        candidate_source, panel, windows, params, return_field, cost_bps
    )
    sandbox = run_sandboxed(script, allowed_imports=allowed_imports, timeout=timeout)
    if sandbox.status != "ok":
        return {"status": sandbox.status, "returns": [], "return_dates": [],
                "violations": list(sandbox.violations), "stderr": sandbox.stderr}
    parsed = parse_backtest_result(sandbox.stdout)
    if parsed is None:
        return {"status": "error", "returns": [], "return_dates": [],
                "stderr": "no backtest result on stdout"}
    return {
        "status": "ok",
        "returns": [float(r) for r in parsed["returns"]],
        "return_dates": [date.fromisoformat(d) for d in parsed.get("return_dates", [])],
    }
