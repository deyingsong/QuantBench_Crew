"""Factor-spanning regression: is the candidate's return just known factors?

Regresses a candidate's realized returns on a factor set (FF5 + momentum) and
reports the spanning alpha and its t-stat. A near-zero, insignificant alpha
against a set that includes the factor the strategy trades means the strategy
delivers nothing the factors don't already — the honest verdict for a
"rediscovered" anomaly. Pure-Python OLS (small k), so no numpy on this path.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

from quantbench_crew.benchmarks.metrics import annualized_sharpe
from quantbench_crew.models import SpanningResult


def _identity(k: int) -> list[list[float]]:
    return [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]


def _inverse(matrix: list[list[float]]) -> list[list[float]]:
    """Gauss-Jordan inverse for a small square matrix."""

    k = len(matrix)
    a = [row[:] + ident_row for row, ident_row in zip(matrix, _identity(k))]
    for col in range(k):
        pivot_row = max(range(col, k), key=lambda r: abs(a[r][col]))
        if abs(a[pivot_row][col]) < 1e-12:
            raise ValueError("singular design matrix (collinear factors?)")
        a[col], a[pivot_row] = a[pivot_row], a[col]
        pivot = a[col][col]
        a[col] = [v / pivot for v in a[col]]
        for r in range(k):
            if r != col and a[r][col] != 0.0:
                factor = a[r][col]
                a[r] = [v - factor * pv for v, pv in zip(a[r], a[col])]
    return [row[k:] for row in a]


def ols(y: Sequence[float], rows: Sequence[Sequence[float]]) -> dict[str, object]:
    """Ordinary least squares; ``rows`` include the leading intercept term."""

    n = len(y)
    k = len(rows[0])
    xtx = [[sum(rows[r][i] * rows[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    xty = [sum(rows[r][i] * y[r] for r in range(n)) for i in range(k)]
    xtx_inv = _inverse(xtx)
    beta = [sum(xtx_inv[i][j] * xty[j] for j in range(k)) for i in range(k)]

    residuals = [y[r] - sum(beta[i] * rows[r][i] for i in range(k)) for r in range(n)]
    ss_res = sum(e * e for e in residuals)
    y_bar = sum(y) / n
    ss_tot = sum((v - y_bar) ** 2 for v in y)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    dof = max(1, n - k)
    sigma2 = ss_res / dof
    tstats = []
    for i in range(k):
        se = (sigma2 * xtx_inv[i][i]) ** 0.5 if xtx_inv[i][i] > 0 else 0.0
        tstats.append(beta[i] / se if se > 0 else 0.0)
    return {"beta": beta, "tstats": tstats, "r_squared": r_squared, "residuals": residuals}


def factor_spanning(
    candidate_by_date: Mapping[date, float],
    factors_by_date: Mapping[date, Mapping[str, float]],
    factor_names: Sequence[str],
    frequency: str,
) -> SpanningResult | None:
    """Regress candidate returns on the named factors; None if too little overlap."""

    dates = sorted(set(candidate_by_date) & set(factors_by_date))
    factor_names = tuple(factor_names)
    if len(dates) <= len(factor_names) + 1:
        return None  # not enough degrees of freedom to estimate

    y = [candidate_by_date[d] for d in dates]
    rows = [[1.0, *(factors_by_date[d][f] for f in factor_names)] for d in dates]
    fit = ols(y, rows)

    beta = fit["beta"]
    tstats = fit["tstats"]
    return SpanningResult(
        factors=factor_names,
        alpha=beta[0],
        alpha_tstat=tstats[0],
        betas={name: beta[i + 1] for i, name in enumerate(factor_names)},
        r_squared=float(fit["r_squared"]),
        residual_sharpe=annualized_sharpe(fit["residuals"], frequency),
    )


def spanning_to_dict(s: SpanningResult) -> dict:
    return {
        "factors": list(s.factors),
        "alpha": s.alpha,
        "alpha_tstat": s.alpha_tstat,
        "betas": dict(s.betas),
        "r_squared": s.r_squared,
        "residual_sharpe": s.residual_sharpe,
    }


def spanning_from_dict(data: dict | None) -> SpanningResult | None:
    if not data:
        return None
    return SpanningResult(
        factors=tuple(data["factors"]),
        alpha=float(data["alpha"]),
        alpha_tstat=float(data["alpha_tstat"]),
        betas={k: float(v) for k, v in data["betas"].items()},
        r_squared=float(data["r_squared"]),
        residual_sharpe=float(data["residual_sharpe"]),
    )
