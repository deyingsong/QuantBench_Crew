"""Significance statistics: deflated Sharpe, capacity, multiple-testing.

The deflated Sharpe ratio (Bailey & Lopez de Prado, 2014) is the project's
sharpest defense against selection bias: it haircuts an observed Sharpe by the
number of trials that produced it and the dispersion of those trials, so a
strategy plucked from a wide search is discounted toward what you'd expect
from luck. The trial count comes from the run manifest — this is where
"count every trial" (Phase 2 principle 6) pays off.

Pure Python; ``statistics.NormalDist`` supplies the normal CDF and its
inverse, so there is no numpy dependency on this path.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from statistics import NormalDist

from quantbench_crew.benchmarks.metrics import periods_per_year
from quantbench_crew.models import CapacityEstimate, DeflatedSharpe

_NORM = NormalDist()
_EULER_MASCHERONI = 0.5772156649015329


def moments(returns: Sequence[float]) -> tuple[float, float, float, float]:
    """Return (mean, std, skew, raw-kurtosis) — kurtosis is 3 for a normal."""

    n = len(returns)
    mean = sum(returns) / n
    var = sum((r - mean) ** 2 for r in returns) / n
    std = math.sqrt(var)
    if std == 0.0:
        return mean, 0.0, 0.0, 3.0
    skew = sum(((r - mean) / std) ** 3 for r in returns) / n
    kurt = sum(((r - mean) / std) ** 4 for r in returns) / n
    return mean, std, skew, kurt


def probabilistic_sharpe_ratio(
    sr: float, sr_benchmark: float, n: int, skew: float, kurt: float
) -> float:
    """P(true per-period SR > benchmark), correcting for skew/kurtosis and n."""

    denom = math.sqrt(max(1e-12, 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr))
    z = (sr - sr_benchmark) * math.sqrt(max(1, n - 1)) / denom
    return _NORM.cdf(z)


def expected_max_sharpe(trial_sr_std: float, n_trials: int) -> float:
    """Expected maximum per-period Sharpe across ``n_trials`` null strategies."""

    if n_trials <= 1 or trial_sr_std <= 0.0:
        return 0.0
    inv1 = _NORM.inv_cdf(1.0 - 1.0 / n_trials)
    inv2 = _NORM.inv_cdf(1.0 - 1.0 / (n_trials * math.e))
    return trial_sr_std * ((1.0 - _EULER_MASCHERONI) * inv1 + _EULER_MASCHERONI * inv2)


def deflated_sharpe_ratio(
    returns: Sequence[float],
    frequency: str,
    n_trials: int,
    trial_sharpes: Sequence[float] = (),
) -> DeflatedSharpe:
    """Deflated Sharpe for a return series given the trial count and trial SRs.

    ``trial_sharpes`` are the *annualized* Sharpes of the strategies tried
    (candidate plus baselines plus generated candidates); their dispersion and
    ``n_trials`` set the benchmark the observed Sharpe must clear.
    """

    n = len(returns)
    mean, std, skew, kurt = moments(returns)
    if std <= 1e-12 or n < 2:  # constant series (float noise tolerance)
        return DeflatedSharpe(0.0, n_trials, 0.0, 1.0, 0.0)

    ppy = periods_per_year(frequency)
    sr = mean / std  # per-period
    observed_annual = sr * math.sqrt(ppy)

    trial_sr_std = _trial_std_per_period(trial_sharpes, ppy)
    sr_star = expected_max_sharpe(trial_sr_std, max(n_trials, 1))
    psr = probabilistic_sharpe_ratio(sr, sr_star, n, skew, kurt)
    deflated_annual = observed_annual * psr
    return DeflatedSharpe(
        observed_sharpe=observed_annual,
        n_trials=n_trials,
        deflated_sharpe=deflated_annual,
        p_value=1.0 - psr,
        haircut=observed_annual - deflated_annual,
    )


def estimate_capacity(
    average_turnover: float,
    median_dollar_vol: float | None = None,
    max_participation: float = 0.10,
) -> CapacityEstimate:
    """First-order capacity proxy from turnover and (optional) median ADV."""

    notes: tuple[str, ...] = ()
    capacity_usd: float | None = None
    if median_dollar_vol and average_turnover > 0:
        # Notional tradable while keeping participation under max_participation.
        capacity_usd = median_dollar_vol * max_participation / average_turnover
    elif median_dollar_vol is None:
        notes = ("no volume data on this dataset; capacity_usd not estimable",)
    return CapacityEstimate(
        average_turnover=average_turnover,
        adv_participation=average_turnover,
        capacity_usd=capacity_usd,
        notes=notes,
    )


def benjamini_hochberg(
    pvalues: Sequence[float], alpha: float = 0.05
) -> tuple[list[bool], float]:
    """Benjamini-Hochberg FDR control; returns (passed mask, threshold)."""

    m = len(pvalues)
    if m == 0:
        return [], 0.0
    order = sorted(range(m), key=lambda i: pvalues[i])
    passed = [False] * m
    threshold = 0.0
    for rank, idx in enumerate(order, start=1):
        if pvalues[idx] <= alpha * rank / m:
            threshold = alpha * rank / m
            for earlier in order[:rank]:
                passed[earlier] = True
    return passed, threshold


def bonferroni(pvalues: Sequence[float], alpha: float = 0.05) -> tuple[list[bool], float]:
    """Bonferroni family-wise correction; returns (passed mask, threshold)."""

    m = max(1, len(pvalues))
    threshold = alpha / m
    return [p <= threshold for p in pvalues], threshold


def deflated_to_dict(d: DeflatedSharpe) -> dict[str, float | int]:
    return {
        "observed_sharpe": d.observed_sharpe,
        "n_trials": d.n_trials,
        "deflated_sharpe": d.deflated_sharpe,
        "p_value": d.p_value,
        "haircut": d.haircut,
    }


def deflated_from_dict(data: dict | None) -> DeflatedSharpe | None:
    if not data:
        return None
    return DeflatedSharpe(
        observed_sharpe=float(data["observed_sharpe"]),
        n_trials=int(data["n_trials"]),
        deflated_sharpe=float(data["deflated_sharpe"]),
        p_value=float(data["p_value"]),
        haircut=float(data["haircut"]),
    )


def capacity_to_dict(c: CapacityEstimate) -> dict:
    return {
        "average_turnover": c.average_turnover,
        "adv_participation": c.adv_participation,
        "capacity_usd": c.capacity_usd,
        "notes": list(c.notes),
    }


def capacity_from_dict(data: dict | None) -> CapacityEstimate | None:
    if not data:
        return None
    return CapacityEstimate(
        average_turnover=float(data["average_turnover"]),
        adv_participation=float(data["adv_participation"]),
        capacity_usd=(None if data.get("capacity_usd") is None else float(data["capacity_usd"])),
        notes=tuple(data.get("notes", ())),
    )


def _trial_std_per_period(trial_sharpes: Sequence[float], ppy: float) -> float:
    values = list(trial_sharpes)
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var) / math.sqrt(ppy)  # annualized SR std -> per-period
