"""QB-14 acceptance: achieved metrics vs ReproductionTarget tolerance bands."""

import math

from quantbench_crew.benchmarks.claims import compare_claim, compare_claims
from quantbench_crew.benchmarks.protocols import (
    evaluate_walk_forward,
    run_walk_forward,
    walk_forward_windows,
)
from quantbench_crew.benchmarks.reference_momentum import build_strategy
from quantbench_crew.datasets import synthetic
from quantbench_crew.models import Claim, Paper, ReproductionTarget

PARAMS = {"formation_periods": 6, "skip_periods": 1, "fraction": 0.3, "field": "return", "seed": 0}


def test_within_tolerance_band() -> None:
    claim = Claim(metric="monthly_return", value=0.0095, tolerance=0.2)
    comparison = compare_claim(claim, {"gross_mean_return": 0.0100})

    assert comparison.within_tolerance
    assert comparison.achieved == 0.0100
    assert "within tolerance" in comparison.note


def test_outside_tolerance_band() -> None:
    claim = Claim(metric="monthly_return", value=0.0095, tolerance=0.2)
    comparison = compare_claim(claim, {"gross_mean_return": 0.05})

    assert not comparison.within_tolerance
    assert "outside tolerance" in comparison.note


def test_metric_aliasing_and_missing_metric() -> None:
    metrics = {"sharpe": 1.2, "gross_mean_return": 0.01}

    sharpe_claim = Claim(metric="Sharpe Ratio", value=1.1, tolerance=0.2)
    assert compare_claim(sharpe_claim, metrics).within_tolerance

    missing = Claim(metric="information_ratio", value=0.5)
    comparison = compare_claim(missing, metrics)
    assert not comparison.within_tolerance
    assert math.isnan(comparison.achieved)
    assert "no achieved metric" in comparison.note


def test_compare_claims_handles_no_target() -> None:
    assert compare_claims(None, {"sharpe": 1.0}) == ()


def test_calibrated_planted_world_reproduces_golden_claim() -> None:
    # Planted spread is 1.4737 * strength; pick strength so the long-short
    # earns ~0.95%/month, matching the golden paper's headline claim.
    strength = 0.0095 / 1.4737
    panel = synthetic.planted_momentum(seed=0, strength=strength, noise=0.0008, n_periods=240)
    windows = walk_forward_windows(panel.dates(), 36, 12, purge=7, embargo=1)
    metrics = evaluate_walk_forward(
        run_walk_forward(build_strategy(PARAMS), panel, windows, cost_bps=10.0), "monthly"
    )

    paper = Paper(title="Momentum", abstract="")
    target = ReproductionTarget(
        paper=paper,
        claims=(Claim(metric="monthly_return", value=0.0095, unit="monthly", tolerance=0.2),),
    )
    comparisons = compare_claims(target, metrics)

    assert len(comparisons) == 1
    assert comparisons[0].within_tolerance, comparisons[0].note
