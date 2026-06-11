"""QB-25: pure-Python OLS and factor-spanning regression."""

import math
from datetime import date

import pytest

from quantbench_crew.benchmarks.spanning import factor_spanning, ols


def test_ols_recovers_exact_linear_relationship() -> None:
    # y = 2 + 3*x1 - 1*x2, no noise.
    rows, y = [], []
    for i in range(20):
        x1 = math.sin(i)
        x2 = math.cos(i * 0.7)
        rows.append([1.0, x1, x2])
        y.append(2.0 + 3.0 * x1 - 1.0 * x2)

    fit = ols(y, rows)
    beta = fit["beta"]
    assert beta[0] == pytest.approx(2.0, abs=1e-6)
    assert beta[1] == pytest.approx(3.0, abs=1e-6)
    assert beta[2] == pytest.approx(-1.0, abs=1e-6)
    assert fit["r_squared"] == pytest.approx(1.0, abs=1e-9)


def _factor_world(n: int = 36) -> dict[date, dict[str, float]]:
    factors = {}
    for i in range(n):
        as_of = date(2015 + i // 12, (i % 12) + 1, 28)
        factors[as_of] = {
            "MKT": 0.01 * math.sin(i),
            "MOM": 0.02 * math.cos(i * 0.9),
        }
    return factors


def test_momentum_candidate_spans_to_mom_with_zero_alpha() -> None:
    factors = _factor_world()
    # Candidate IS the momentum factor: alpha 0, MOM beta 1, MKT beta 0.
    candidate = {d: vals["MOM"] for d, vals in factors.items()}

    spanning = factor_spanning(candidate, factors, ["MKT", "MOM"], "monthly")

    assert spanning is not None
    assert spanning.betas["MOM"] == pytest.approx(1.0, abs=1e-6)
    assert spanning.betas["MKT"] == pytest.approx(0.0, abs=1e-6)
    assert spanning.alpha == pytest.approx(0.0, abs=1e-6)
    assert spanning.r_squared == pytest.approx(1.0, abs=1e-9)


def test_genuine_alpha_is_detected() -> None:
    factors = _factor_world()
    # Candidate has a constant edge on top of the factor exposure.
    candidate = {d: 0.01 + vals["MOM"] for d, vals in factors.items()}

    spanning = factor_spanning(candidate, factors, ["MKT", "MOM"], "monthly")

    assert spanning.alpha == pytest.approx(0.01, abs=1e-6)
    assert abs(spanning.alpha_tstat) > 2.0  # significant


def test_too_little_overlap_returns_none() -> None:
    factors = _factor_world(3)
    candidate = {d: 0.0 for d in factors}
    assert factor_spanning(candidate, factors, ["MKT", "MOM"], "monthly") is None
