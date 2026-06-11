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

from datetime import date
from pathlib import Path

from quantbench_crew.benchmarks.contract import PanelData

DEFAULT_FIXTURE = Path("data/raw/french_momentum_monthly.csv")


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


def _period_to_date(period: str) -> date:
    year = int(period[:4])
    month = int(period[4:6])
    return date(year, month, 28)
