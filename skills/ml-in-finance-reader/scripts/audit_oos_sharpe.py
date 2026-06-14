#!/usr/bin/env python3
"""Recompute diagnostics for a dated out-of-sample strategy return series."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class AuditResult:
    observations: int
    first_date: str
    last_date: str
    periods_per_year: float
    annual_risk_free_rate: float
    mean_periodic_return: float
    periodic_volatility: float
    annualized_arithmetic_excess_return: float
    annualized_geometric_return: float
    annualized_sharpe: float
    newey_west_lags: int
    newey_west_t_stat_mean_excess: float
    max_drawdown: float
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit Sharpe and related diagnostics on a dated return series. "
            "This does not prove that the supplied returns are truly out of sample."
        )
    )
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--return-column", required=True)
    parser.add_argument("--date-column", default="date")
    parser.add_argument("--test-start", help="Inclusive ISO date or timestamp.")
    parser.add_argument("--test-end", help="Inclusive ISO date or timestamp.")
    parser.add_argument("--periods-per-year", type=float, default=252.0)
    parser.add_argument("--annual-risk-free-rate", type=float, default=0.0)
    parser.add_argument(
        "--nw-lags",
        type=int,
        help="Newey-West lags. Default uses floor(4 * (n / 100)^(2/9)).",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def parse_datetime(value: str, label: str) -> datetime:
    cleaned = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError(f"invalid {label} ISO date or timestamp: {value!r}") from exc


def load_rows(
    path: Path, date_column: str, return_column: str
) -> tuple[list[tuple[datetime, float]], list[str]]:
    warnings: list[str] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        missing = {date_column, return_column} - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {sorted(missing)}")

        rows: list[tuple[datetime, float]] = []
        for line_number, row in enumerate(reader, start=2):
            date = parse_datetime(row[date_column], f"date at line {line_number}")
            try:
                value = float(row[return_column])
            except ValueError as exc:
                raise ValueError(
                    f"invalid return at line {line_number}: {row[return_column]!r}"
                ) from exc
            if not math.isfinite(value):
                raise ValueError(f"non-finite return at line {line_number}")
            if value < -1.0:
                raise ValueError(
                    f"simple return below -100% at line {line_number}: {value}"
                )
            rows.append((date, value))

    if not rows:
        raise ValueError("CSV contains no data rows")
    input_dates = [date for date, _ in rows]
    if input_dates != sorted(input_dates):
        warnings.append("Input dates were not sorted; calculations use chronological order.")
    if len(input_dates) != len(set(input_dates)):
        warnings.append(
            "Duplicate timestamps detected; verify aggregation and overlapping positions."
        )
    rows.sort(key=lambda item: item[0])
    return rows, warnings


def filter_rows(
    rows: list[tuple[datetime, float]],
    test_start: str | None,
    test_end: str | None,
    warnings: list[str],
) -> list[tuple[datetime, float]]:
    start = parse_datetime(test_start, "test-start") if test_start else None
    end = parse_datetime(test_end, "test-end") if test_end else None
    if start and end and start > end:
        raise ValueError("test-start must be no later than test-end")
    if start is None and end is None:
        warnings.append(
            "No explicit OOS date filter supplied; the script cannot verify OOS status."
        )
    selected = [
        row
        for row in rows
        if (start is None or row[0] >= start) and (end is None or row[0] <= end)
    ]
    if len(selected) < 2:
        raise ValueError("selected date range must contain at least two observations")
    return selected


def newey_west_t_stat(values: list[float], lags: int) -> float:
    n = len(values)
    mean = statistics.fmean(values)
    centered = [value - mean for value in values]
    long_run_variance = sum(value * value for value in centered) / n
    for lag in range(1, lags + 1):
        covariance = sum(
            centered[index] * centered[index - lag] for index in range(lag, n)
        ) / n
        weight = 1.0 - lag / (lags + 1.0)
        long_run_variance += 2.0 * weight * covariance
    variance_of_mean = max(long_run_variance, 0.0) / n
    if variance_of_mean == 0.0:
        return math.inf if mean > 0 else -math.inf if mean < 0 else math.nan
    return mean / math.sqrt(variance_of_mean)


def max_drawdown(returns: list[float]) -> float:
    wealth = 1.0
    peak = 1.0
    worst = 0.0
    for value in returns:
        wealth *= 1.0 + value
        peak = max(peak, wealth)
        worst = min(worst, wealth / peak - 1.0)
    return worst


def geometric_return(returns: list[float], periods_per_year: float) -> float:
    log_wealth = 0.0
    for value in returns:
        if value == -1.0:
            return -1.0
        log_wealth += math.log1p(value)
    return math.expm1(log_wealth * periods_per_year / len(returns))


def audit(args: argparse.Namespace) -> AuditResult:
    if args.periods_per_year <= 0:
        raise ValueError("periods-per-year must be positive")
    if args.annual_risk_free_rate <= -1.0:
        raise ValueError("annual-risk-free-rate must be greater than -1")

    rows, warnings = load_rows(args.csv_path, args.date_column, args.return_column)
    selected = filter_rows(rows, args.test_start, args.test_end, warnings)
    returns = [value for _, value in selected]

    n = len(returns)
    if n < args.periods_per_year:
        warnings.append(
            "Selected range contains less than one nominal year; annualized metrics "
            "may be unstable."
        )
    lags = (
        math.floor(4.0 * (n / 100.0) ** (2.0 / 9.0))
        if args.nw_lags is None
        else args.nw_lags
    )
    if lags < 0:
        raise ValueError("nw-lags cannot be negative")
    if lags >= n:
        warnings.append(f"Newey-West lags reduced from {lags} to {n - 1}.")
        lags = n - 1

    periodic_rf = math.expm1(math.log1p(args.annual_risk_free_rate) / args.periods_per_year)
    excess = [value - periodic_rf for value in returns]
    mean_return = statistics.fmean(returns)
    mean_excess = statistics.fmean(excess)
    volatility = statistics.stdev(returns)
    if volatility == 0.0:
        sharpe = math.inf if mean_excess > 0 else -math.inf if mean_excess < 0 else math.nan
        warnings.append("Periodic volatility is zero; Sharpe is not finite.")
    else:
        sharpe = mean_excess / volatility * math.sqrt(args.periods_per_year)

    warnings.append(
        "Overlapping returns and hidden model-selection trials are not detectable from this CSV."
    )
    return AuditResult(
        observations=n,
        first_date=selected[0][0].isoformat(),
        last_date=selected[-1][0].isoformat(),
        periods_per_year=args.periods_per_year,
        annual_risk_free_rate=args.annual_risk_free_rate,
        mean_periodic_return=mean_return,
        periodic_volatility=volatility,
        annualized_arithmetic_excess_return=mean_excess * args.periods_per_year,
        annualized_geometric_return=geometric_return(returns, args.periods_per_year),
        annualized_sharpe=sharpe,
        newey_west_lags=lags,
        newey_west_t_stat_mean_excess=newey_west_t_stat(excess, lags),
        max_drawdown=max_drawdown(returns),
        warnings=warnings,
    )


def print_human(result: AuditResult) -> None:
    print(f"Observations: {result.observations}")
    print(f"Selected range: {result.first_date} to {result.last_date}")
    print(f"Periods/year: {result.periods_per_year:g}")
    print(f"Mean periodic return: {result.mean_periodic_return:.8f}")
    print(f"Periodic volatility: {result.periodic_volatility:.8f}")
    print(
        "Annualized arithmetic excess return: "
        f"{result.annualized_arithmetic_excess_return:.8f}"
    )
    print(f"Annualized geometric return: {result.annualized_geometric_return:.8f}")
    print(f"Annualized Sharpe: {result.annualized_sharpe:.8f}")
    print(
        f"Newey-West t-stat (lags={result.newey_west_lags}): "
        f"{result.newey_west_t_stat_mean_excess:.8f}"
    )
    print(f"Max drawdown: {result.max_drawdown:.8f}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")


def main() -> int:
    args = parse_args()
    try:
        result = audit(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(asdict(result), indent=2, allow_nan=True))
    else:
        print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
