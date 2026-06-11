"""Claim comparison: achieved metrics versus the paper's stated targets.

Maps each :class:`Claim` in a :class:`ReproductionTarget` onto an achieved
metric and tests it against the claim's relative tolerance band. This is a
*sanity band*, not the optimization objective — scoring code toward the
paper's number would invite p-hacking the reproduction (see the design note's
Goodhart risk). The comparison is reported, never optimized against.
"""

from __future__ import annotations

from collections.abc import Mapping

from quantbench_crew.models import Claim, ClaimComparison, ReproductionTarget

# Paper metric names -> achieved-metric keys produced by the walk-forward eval.
# Monthly data makes the per-period mean the monthly return directly.
_METRIC_ALIASES = {
    "monthly_return": "gross_mean_return",
    "mean_return": "gross_mean_return",
    "return": "gross_mean_return",
    "annual_return": "annualized_return",
    "annualized_return": "annualized_return",
    "sharpe": "sharpe",
    "sharpe_ratio": "sharpe",
    "volatility": "volatility",
    "max_drawdown": "max_drawdown",
}


def achieved_for_claim(claim: Claim, metrics: Mapping[str, float]) -> float | None:
    """Resolve the achieved value for a claim's metric, or None if absent."""

    normalized = claim.metric.lower().strip().replace(" ", "_")
    key = _METRIC_ALIASES.get(normalized)
    if key is None or key not in metrics:
        return None
    return float(metrics[key])


def compare_claim(claim: Claim, metrics: Mapping[str, float]) -> ClaimComparison:
    achieved = achieved_for_claim(claim, metrics)
    if achieved is None:
        return ClaimComparison(
            claim=claim,
            achieved=float("nan"),
            within_tolerance=False,
            note=f"no achieved metric mapped for {claim.metric!r}",
        )
    band = abs(claim.value) * claim.tolerance
    within = abs(achieved - claim.value) <= band
    note = (
        f"achieved {achieved:.4f} vs claimed {claim.value:.4f} "
        f"(±{band:.4f}): {'within' if within else 'outside'} tolerance"
    )
    return ClaimComparison(
        claim=claim, achieved=achieved, within_tolerance=within, note=note
    )


def compare_claims(
    target: ReproductionTarget | None, metrics: Mapping[str, float]
) -> tuple[ClaimComparison, ...]:
    """Compare every claim in the target against the achieved metrics."""

    if target is None:
        return ()
    return tuple(compare_claim(claim, metrics) for claim in target.claims)
