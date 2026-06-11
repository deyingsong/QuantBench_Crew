"""Kenneth French data library loader (free, public momentum portfolios).

Live download is added behind ``fetcher`` later; for now the loader reads a
cached CSV fixture so the golden-paper run is offline and deterministic. The
French momentum file ships decile/extreme portfolio returns in *percent*; we
normalize to decimals and expose them as a ``PanelData`` whose assets are the
portfolio buckets (e.g. ``Lo PRIOR``/``Hi PRIOR``), so the reference momentum
strategy and the claim comparison operate on the same monthly return units as
the paper.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from quantbench_crew.benchmarks.contract import PanelData

DEFAULT_FIXTURE = Path("data/raw/french_momentum_monthly.csv")
DEFAULT_FF_FIXTURE = Path("data/raw/ff_factors_monthly.csv")
FF_FACTOR_NAMES = ("MKT", "SMB", "HML", "RMW", "CMA", "MOM")


def load_french_momentum(path: str | Path = DEFAULT_FIXTURE) -> PanelData:
    """Load a cached French momentum CSV into monthly PanelData (decimals)."""

    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"French momentum fixture not found at {csv_path}. Live download "
            "is not wired yet; provide the cached CSV or use a synthetic world."
        )
    return parse_french_csv(csv_path.read_text(encoding="utf-8"))


def parse_french_csv(text: str) -> PanelData:
    """Parse the French long-format CSV: YYYYMM,portfolio,return_pct."""

    records = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = [field.strip() for field in line.split(",")]
        if len(fields) != 3 or fields[0].lower() in ("date", "yyyymm"):
            continue
        period, portfolio, value = fields
        records.append((_period_to_date(period), portfolio, {"return": float(value) / 100.0}))
    if not records:
        raise ValueError("No usable rows parsed from French CSV fixture.")
    return PanelData.from_records(records)


def load_ff_factors(path: str | Path = DEFAULT_FF_FIXTURE) -> dict[date, dict[str, float]]:
    """Load monthly FF5+momentum factors keyed by month-end date (decimals).

    Wide CSV: a ``YYYYMM`` (or ``date``) column plus one column per factor,
    returns in percent. Column names are taken from the header, so any factor
    subset works; values normalize to decimals to match strategy returns.
    """

    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(
            f"French factor file not found at {csv_path}. Provide the cached "
            "FF5+MOM CSV (YYYYMM plus factor columns, in percent)."
        )
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(row for row in handle if not row.lstrip().startswith("#"))
        header = next(reader)
        date_col = header[0]
        factor_cols = header[1:]
        out: dict[date, dict[str, float]] = {}
        for row in reader:
            if not row or not row[0].strip() or row[0].strip().lower() in ("date", date_col.lower()):
                continue
            as_of = _period_to_date(row[0].strip())
            out[as_of] = {
                name: float(value) / 100.0
                for name, value in zip(factor_cols, row[1:])
                if value.strip()
            }
    if not out:
        raise ValueError("No usable rows parsed from French factor file.")
    return out


def _period_to_date(period: str) -> date:
    period = period.replace("-", "")
    year = int(period[:4])
    month = int(period[4:6])
    return date(year, month, 28)
