"""The curated evaluation set (QB-34).

Each case pins a hand-labeled reproduction target and the outcome the system
*should* reach on it. The set deliberately mixes strong synthetic signal, a
pure-noise negative control that must never reproduce, and real CRSP cases
whose honest 2015-2024 outcome is encoded as ground truth — so a code change
that makes the system over-claim (or stop reproducing real signal) turns a
case red.

Composition (operator-confirmed, Phase 2):
- ``momentum_planted``  — synthetic, strong signal              -> reproduces
- ``noise_control``     — synthetic pure noise (negative ctrl)  -> does_not_reproduce
- ``momentum_crsp``     — Jegadeesh-Titman on real CRSP 2015-24 -> does_not_reproduce
                          (the 0.95%/mo premium did not persist at magnitude)
- ``gkx_ml_crsp``       — GKX-style linear cross-section on CRSP -> does_not_reproduce

The value/profitability (Compustat) and full-sklearn ML cases are out of scope
until that data / dependency is supplied; see docs/phase2-design.md.
"""

from __future__ import annotations

from quantbench_crew.models import Claim, EvalCase, Paper, ReproductionTarget

# Planted spread is ~1.4737 * strength; pick strength so the long-short earns
# ~0.95%/month, matching the momentum headline claim.
_PLANTED_STRENGTH = 0.0095 / 1.4737


def _target(paper: Paper, metric: str, value: float, *, tolerance: float = 0.2) -> ReproductionTarget:
    return ReproductionTarget(
        paper=paper,
        claims=(Claim(metric=metric, value=value, unit="monthly", tolerance=tolerance),),
    )


def build_eval_set() -> list[EvalCase]:
    momentum_paper = Paper(
        title="Returns to Buying Winners and Selling Losers (reproduction)",
        abstract="Cross-sectional momentum; ~0.95% per month winner-minus-loser.",
    )
    gkx_paper = Paper(
        title="Empirical Asset Pricing via Machine Learning (GKX-style, price/volume subset)",
        abstract="Cross-sectional ML predictability of monthly equity returns.",
    )

    return [
        EvalCase(
            slug="momentum_planted",
            paper=momentum_paper,
            data_tier="synthetic",
            expected_outcome="reproduces",
            targets=_target(momentum_paper, "monthly_return", 0.0095),
            strategy="momentum",
            dataset="planted_momentum",
            dataset_params={
                "strength": _PLANTED_STRENGTH,
                "noise": 0.0008,
                "n_periods": 240,
                "seed": 0,
            },
            notes=("strong planted signal; must clear every rigor bar",),
        ),
        EvalCase(
            slug="noise_control",
            paper=Paper(title="Placebo Momentum (negative control)", abstract="No signal."),
            data_tier="synthetic",
            expected_outcome="does_not_reproduce",
            targets=_target(
                Paper(title="Placebo Momentum (negative control)", abstract=""),
                "monthly_return",
                0.0095,
            ),
            strategy="momentum",
            dataset="pure_noise",
            dataset_params={"n_periods": 240, "seed": 0},
            notes=("the noise gate generalized: a plausible claim on signal-free data",),
        ),
        EvalCase(
            slug="momentum_crsp",
            paper=momentum_paper,
            data_tier="crsp",
            expected_outcome="does_not_reproduce",
            targets=_target(momentum_paper, "monthly_return", 0.0095),
            strategy="momentum",
            dataset="crsp",
            dataset_params={},
            notes=("S&P 500 universe 2015-2024; momentum was a weak decade",),
        ),
        EvalCase(
            slug="gkx_ml_crsp",
            paper=gkx_paper,
            data_tier="crsp",
            expected_outcome="does_not_reproduce",
            targets=_target(gkx_paper, "monthly_return", 0.0095),
            strategy="ml",
            dataset="crsp",
            dataset_params={},
            notes=("linear cross-sectional predictor on price/volume characteristics",),
        ),
    ]
