"""QB-22 acceptance: CRSP CIZ loader — compounding, survivorship, filters."""

import csv
from datetime import date
from pathlib import Path

import pytest

from quantbench_crew.benchmarks import build_strategy, run_backtest
from quantbench_crew.datasets import crsp
from quantbench_crew.datasets.registry import load_dataset, panel_hash

DAILY_HEADER = [
    "PERMNO", "DlyCalDt", "DlyRet", "DlyCap", "DlyPrc", "DlyPrcVol",
    "PrimaryExch", "SecurityType", "ShareType",
]
MONTHS = [f"2015-{m:02d}" for m in range(1, 9)]  # 2015-01 .. 2015-08


def _daily_rows(permno, months, ret, cap, price, sectype="EQTY", share="NS", exch="N"):
    rows = []
    for ym in months:
        for day in ("05", "20"):
            rows.append([permno, f"{ym}-{day}", ret, cap, price, "1000000", exch, sectype, share])
    return rows


def _write_daily(tmp_path: Path, rows) -> Path:
    path = tmp_path / "daily.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(DAILY_HEADER)
        w.writerows(rows)
    return path


def _write_delisting(tmp_path: Path, rows) -> Path:
    path = tmp_path / "delist.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["PERMNO", "DelistingDt", "DelRet"])
        w.writerows(rows)
    return path


def _standard_universe(tmp_path: Path):
    rows = []
    rows += _daily_rows("10001", MONTHS, "0.01", "5000000", "100.0")    # winner
    rows += _daily_rows("10002", MONTHS, "0.0", "4000000", "80.0")      # flat
    rows += _daily_rows("10003", MONTHS[:5], "-0.01", "3000000", "60.0")  # delists 2015-05
    return _write_daily(tmp_path, rows)


def test_monthly_return_compounds_daily(tmp_path: Path) -> None:
    daily = _write_daily(tmp_path, _daily_rows("10001", ["2015-01"], "0.01", "5000000", "100.0"))
    panel = crsp.load_crsp(daily, None)

    as_of = panel.dates()[0]
    # two daily returns of 1% compound to (1.01^2 - 1).
    assert panel.value(as_of, "10001", "return") == pytest.approx(1.01 * 1.01 - 1.0)
    assert as_of == date(2015, 1, 20)  # canonical month-end = last trading day
    assert panel.value(as_of, "10001", "cap") == pytest.approx(5_000_000)


def test_survivorship_free_by_construction(tmp_path: Path) -> None:
    daily = _standard_universe(tmp_path)
    panel = crsp.load_crsp(daily, None)

    # 10003 trades only through 2015-05; later months must not contain it.
    may = date(2015, 5, 20)
    aug = date(2015, 8, 20)
    assert "10003" in {a for a in panel.assets()}
    assert panel.value(may, "10003", "return") is not None
    assert panel.value(aug, "10003", "return") is None
    # No look-ahead: a panel as of March has no later months.
    truncated = panel.up_to(date(2015, 3, 20))
    assert all(d <= date(2015, 3, 20) for d in truncated.dates())


def test_delisting_return_is_spliced(tmp_path: Path) -> None:
    daily = _standard_universe(tmp_path)
    delist = _write_delisting(tmp_path, [["10003", "2015-05-29", "-0.30"]])

    without = crsp.load_crsp(daily, None)
    with_del = crsp.load_crsp(daily, delist)

    may = date(2015, 5, 20)
    base = without.value(may, "10003", "return")  # (0.99^2 - 1)
    spliced = with_del.value(may, "10003", "return")
    # Delisting return compounds into the final month: (1+base)*(1-0.30)-1.
    assert spliced == pytest.approx((1.0 + base) * (1.0 - 0.30) - 1.0)
    assert spliced < base


def test_filters_exclude_non_common_and_wrong_exchange(tmp_path: Path) -> None:
    rows = _daily_rows("10001", ["2015-01"], "0.01", "5000000", "100.0")
    rows += _daily_rows("20001", ["2015-01"], "0.05", "1000", "10.0", sectype="FUND")
    rows += _daily_rows("20002", ["2015-01"], "0.05", "1000", "10.0", exch="R")
    daily = _write_daily(tmp_path, rows)

    panel = crsp.load_crsp(daily, None)
    assert set(panel.assets()) == {"10001"}  # FUND and exchange "R" filtered out


def test_microcap_and_price_filters(tmp_path: Path) -> None:
    rows = _daily_rows("10001", ["2015-01"], "0.01", "5000000", "100.0")
    rows += _daily_rows("10002", ["2015-01"], "0.01", "1000", "2.0")  # tiny cap, low price
    daily = _write_daily(tmp_path, rows)

    by_price = crsp.load_crsp(daily, None, min_price=5.0)
    assert set(by_price.assets()) == {"10001"}  # 10002 below $5

    by_cap = crsp.load_crsp(daily, None, cap_percentile=0.5)
    assert set(by_cap.assets()) == {"10001"}  # bottom-half cap dropped


def test_reference_momentum_runs_on_crsp_panel(tmp_path: Path) -> None:
    daily = _standard_universe(tmp_path)
    panel = crsp.load_crsp(daily, None)

    strategy = build_strategy({"formation_periods": 2, "skip_periods": 1, "fraction": 0.34})
    returns = run_backtest(strategy, panel)

    assert returns  # produced out-of-sample portfolio returns end to end
    # Persistent winner (10001) over loser; long-short momentum is positive.
    assert sum(returns) / len(returns) > 0


def test_registry_crsp_tier_is_hashed(tmp_path: Path) -> None:
    daily = _standard_universe(tmp_path)
    loaded = load_dataset("crsp", {"daily_path": daily, "delisting_path": None})

    assert loaded.name == "crsp"
    assert loaded.frequency == "monthly"
    assert loaded.content_hash == panel_hash(loaded.panel)


def test_cache_round_trip_preserves_panel(tmp_path: Path) -> None:
    daily = _standard_universe(tmp_path)
    cache = tmp_path / "crsp_monthly.csv"

    built = crsp.load_crsp(daily, None, cache_path=cache)
    assert cache.exists()
    cached = crsp.load_crsp(daily, None, cache_path=cache)

    assert panel_hash(built) == panel_hash(cached)


def test_missing_required_column_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("PERMNO,DlyCalDt\n10001,2015-01-05\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        crsp.load_crsp(path, None)
