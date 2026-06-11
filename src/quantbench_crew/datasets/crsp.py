"""CRSP CIZ daily flat-file loader: point-in-time monthly PanelData.

Streams the daily security file (one row per PERMNO-day) once with the stdlib
``csv`` reader — no pandas, no full-file load — and aggregates to a monthly
panel keyed by PERMNO. Pure-stdlib keeps the loader deterministic and in the
bit-exact tier; numpy/sklearn (the optional ``numeric`` group) are reserved
for the ML *model*, not the data build.

Survivorship-bias-free by construction: the daily file is realized history,
so a delisted security simply has no rows after it leaves — the panel never
contains a name that was not actually trading. The one adjustment is splicing
the delisting return (``DelRet``) into the security's final month, so an
investor's loss on a delisting is recorded rather than silently dropped.

No look-ahead: a month's cell is built only from that month's daily rows;
``PanelData.up_to(t)`` then exposes only months <= t.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date
from math import sqrt
from pathlib import Path
from typing import Any, Iterable, Mapping

from quantbench_crew.benchmarks.contract import PanelData

DEFAULT_DAILY_PATH = Path("data/raw/stock/daily_stock_file_15-24.csv")
DEFAULT_DELISTING_PATH = Path("data/raw/stock/delisting_information_15-24.csv")

# US common stock on the major exchanges (see the data inventory in
# docs/phase2-design.md). Empty/None on any axis disables that filter.
DEFAULT_SECURITY_TYPES = ("EQTY",)
DEFAULT_SHARE_TYPES = ("NS",)
DEFAULT_EXCHANGES = ("N", "A", "Q")

# Output characteristic fields per (PERMNO, month).
PANEL_FIELDS = ("return", "cap", "price", "dollar_vol", "std_ret", "max_ret", "n_days")


@dataclass
class _Cell:
    comp: float = 1.0          # product of (1 + daily return)
    n: int = 0
    sum_r: float = 0.0
    sumsq_r: float = 0.0
    max_r: float = float("-inf")
    last_date: str = ""
    last_cap: float = 0.0
    last_price: float = 0.0
    dollar_vol: float = 0.0


def load_crsp(
    daily_path: str | Path = DEFAULT_DAILY_PATH,
    delisting_path: str | Path | None = DEFAULT_DELISTING_PATH,
    *,
    security_types: Iterable[str] | None = DEFAULT_SECURITY_TYPES,
    share_types: Iterable[str] | None = DEFAULT_SHARE_TYPES,
    exchanges: Iterable[str] | None = DEFAULT_EXCHANGES,
    min_price: float = 0.0,
    cap_percentile: float = 0.0,
    cache_path: str | Path | None = None,
) -> PanelData:
    """Build a monthly point-in-time ``PanelData`` from CRSP CIZ daily files."""

    if cache_path is not None and Path(cache_path).exists():
        return _from_monthly_csv(Path(cache_path))

    sec = _as_set(security_types)
    shr = _as_set(share_types)
    exch = _as_set(exchanges)

    cells: dict[tuple[str, str], _Cell] = {}
    month_end: dict[str, str] = {}  # "YYYY-MM" -> max trading date seen

    with open(daily_path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        ix = _index(next(reader), (
            "PERMNO", "DlyCalDt", "DlyRet", "DlyCap", "DlyPrc", "DlyPrcVol",
            "PrimaryExch", "SecurityType", "ShareType",
        ))
        for row in reader:
            if sec and row[ix["SecurityType"]] not in sec:
                continue
            if shr and row[ix["ShareType"]] not in shr:
                continue
            if exch and row[ix["PrimaryExch"]] not in exch:
                continue

            permno = row[ix["PERMNO"]]
            day = row[ix["DlyCalDt"]]
            ym = day[:7]
            cell = cells.get((permno, ym))
            if cell is None:
                cell = cells[(permno, ym)] = _Cell()

            ret = _to_float(row[ix["DlyRet"]])
            if ret is not None:
                cell.comp *= 1.0 + ret
                cell.n += 1
                cell.sum_r += ret
                cell.sumsq_r += ret * ret
                cell.max_r = max(cell.max_r, ret)
            cell.dollar_vol += _to_float(row[ix["DlyPrcVol"]]) or 0.0
            if day >= cell.last_date:  # month-end snapshot
                cell.last_date = day
                cell.last_cap = _to_float(row[ix["DlyCap"]]) or 0.0
                cell.last_price = abs(_to_float(row[ix["DlyPrc"]]) or 0.0)
            if day > month_end.get(ym, ""):
                month_end[ym] = day

    _splice_delistings(delisting_path, cells, month_end)
    records = _build_records(cells, month_end, min_price, cap_percentile)
    panel = PanelData.from_records(records)

    if cache_path is not None:
        _to_monthly_csv(Path(cache_path), records)
    return panel


def _splice_delistings(
    delisting_path: str | Path | None,
    cells: dict[tuple[str, str], _Cell],
    month_end: dict[str, str],
) -> None:
    if delisting_path is None or not Path(delisting_path).exists():
        return
    with open(delisting_path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        ix = _index(next(reader), ("PERMNO", "DelistingDt", "DelRet"))
        for row in reader:
            delret = _to_float(row[ix["DelRet"]])
            if delret is None:
                continue
            permno = row[ix["PERMNO"]]
            ym = row[ix["DelistingDt"]][:7]
            key = (permno, ym)
            cell = cells.get(key)
            if cell is None:
                # Delisted in a month with no surviving daily rows: the month's
                # whole return is the delisting return.
                cell = cells[key] = _Cell()
                month_end.setdefault(ym, row[ix["DelistingDt"]])
            cell.comp *= 1.0 + delret


def _build_records(
    cells: Mapping[tuple[str, str], _Cell],
    month_end: Mapping[str, str],
    min_price: float,
    cap_percentile: float,
) -> list[tuple[date, str, dict[str, float]]]:
    # Group by month so the microcap percentile filter is cross-sectional.
    by_month: dict[str, list[tuple[str, _Cell]]] = {}
    for (permno, ym), cell in cells.items():
        if min_price and cell.last_price < min_price:
            continue
        by_month.setdefault(ym, []).append((permno, cell))

    records: list[tuple[date, str, dict[str, float]]] = []
    for ym, entries in by_month.items():
        as_of = date.fromisoformat(month_end[ym])
        kept = _drop_microcaps(entries, cap_percentile)
        for permno, cell in kept:
            records.append((as_of, permno, _fields(cell)))
    return records


def _drop_microcaps(
    entries: list[tuple[str, _Cell]], cap_percentile: float
) -> list[tuple[str, _Cell]]:
    if cap_percentile <= 0.0:
        return entries
    ranked = sorted(entries, key=lambda item: item[1].last_cap)
    cutoff = int(len(ranked) * cap_percentile)
    return ranked[cutoff:]


def _fields(cell: _Cell) -> dict[str, float]:
    std = 0.0
    if cell.n > 1:
        var = (cell.sumsq_r - cell.sum_r * cell.sum_r / cell.n) / (cell.n - 1)
        std = sqrt(var) if var > 0 else 0.0
    return {
        "return": cell.comp - 1.0,
        "cap": cell.last_cap,
        "price": cell.last_price,
        "dollar_vol": cell.dollar_vol,
        "std_ret": std,
        "max_ret": cell.max_r if cell.max_r != float("-inf") else 0.0,
        "n_days": float(cell.n),
    }


def _index(header: list[str], needed: Iterable[str]) -> dict[str, int]:
    positions = {name: i for i, name in enumerate(header)}
    missing = [name for name in needed if name not in positions]
    if missing:
        raise ValueError(f"CRSP file missing required columns: {missing}")
    return {name: positions[name] for name in needed}


def _to_float(value: str) -> float | None:
    value = value.strip()
    if not value or value in ("NA", "NaN", "."):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _as_set(values: Iterable[str] | None) -> set[str]:
    return set(values) if values else set()


def _to_monthly_csv(
    path: Path, records: list[tuple[date, str, dict[str, float]]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("date", "permno", *PANEL_FIELDS))
        for as_of, permno, fields in sorted(records, key=lambda r: (r[0], r[1])):
            writer.writerow((as_of.isoformat(), permno, *(fields[f] for f in PANEL_FIELDS)))


def _from_monthly_csv(path: Path) -> PanelData:
    records: list[tuple[date, str, dict[str, float]]] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            fields = {name: float(row[name]) for name in PANEL_FIELDS}
            records.append((date.fromisoformat(row["date"]), row["permno"], fields))
    return PanelData.from_records(records)
