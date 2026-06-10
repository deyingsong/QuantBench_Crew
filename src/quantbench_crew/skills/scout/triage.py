"""Reproducibility triage: data-tier classification and feasibility gating.

The rubric follows scholar-evaluation criteria — data accessibility, claim
falsifiability, released code — specialized to quant data tiers: vendor names
like CRSP or TAQ imply licensed (WRDS-style) access, so they cap feasibility
below public-data papers, and proprietary/internal data caps it near zero.
Deterministic and offline by construction; it is its own fallback.
"""

from __future__ import annotations

import re
from typing import Any

from quantbench_crew.models import Paper
from quantbench_crew.skills import register_skill
from quantbench_crew.skills.base import RunContext, SkillResult, skill_settings

PROPRIETARY_MARKERS = (
    "proprietary",
    "internal data",
    "confidential",
    "order-level data",
    "broker-provided",
    "non-public",
)

VENDOR_MARKERS = (
    "crsp",
    "compustat",
    "taq",
    "optionmetrics",
    "ibes",
    "wrds",
    "bloomberg",
    "refinitiv",
    "datastream",
    "morningstar",
    "trace",
)

PUBLIC_MARKERS = (
    "kenneth french",
    "ken french",
    "french data library",
    "fama-french",
    "fred",
    "yahoo finance",
    "publicly available",
    "open data",
    "kaggle",
)

CODE_MARKERS = (
    "github.com",
    "gitlab.com",
    "code is available",
    "code available",
    "replication code",
    "open source",
    "open-source",
)

# Worst detected tier wins; papers naming no data source at all sit between
# public and vendor because the requirement is unknown, not because it is met.
TIER_BASE_SCORE = {"public": 0.9, "unknown": 0.6, "vendor": 0.4, "proprietary": 0.1}

CODE_BONUS = 0.1
FALSIFIABILITY_BONUS = 0.05
DEFAULT_THRESHOLD = 0.5

_NUMERIC_CLAIM = re.compile(r"\d+(?:\.\d+)?\s*(?:%|percent)|sharpe ratios? of\s*\d", re.IGNORECASE)


class ReproducibilityTriageSkill:
    """Classify data requirements and score feasibility to gate spend."""

    name = "reproducibility_triage"

    def available(self) -> bool:
        return True

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        paper: Paper = inputs["paper"]
        settings = skill_settings(ctx.config, "quant_scout", self.name)
        threshold = float(settings.get("threshold", DEFAULT_THRESHOLD))

        text = " ".join(
            (paper.title, paper.abstract, " ".join(paper.keywords))
        ).lower()
        matched = {
            "proprietary": [m for m in PROPRIETARY_MARKERS if m in text],
            "vendor": [m for m in VENDOR_MARKERS if m in text],
            "public": [m for m in PUBLIC_MARKERS if m in text],
        }
        if matched["proprietary"]:
            tier = "proprietary"
        elif matched["vendor"]:
            tier = "vendor"
        elif matched["public"]:
            tier = "public"
        else:
            tier = "unknown"

        code_released = any(marker in text for marker in CODE_MARKERS)
        falsifiable = bool(_NUMERIC_CLAIM.search(text))
        feasibility = min(
            1.0,
            TIER_BASE_SCORE[tier]
            + (CODE_BONUS if code_released else 0.0)
            + (FALSIFIABILITY_BONUS if falsifiable else 0.0),
        )
        passes_gate = feasibility >= threshold

        notes = (
            f"data tier {tier!r}"
            + (f" via markers {matched[tier]}" if tier in matched and matched[tier] else ""),
            f"code released: {code_released}; quantitative claims: {falsifiable}",
            f"feasibility {feasibility:.2f} vs threshold {threshold:.2f}: "
            + ("passes gate" if passes_gate else "gated out"),
        )
        result = SkillResult(
            skill=self.name,
            status="ok",
            payload={
                "data_tier": tier,
                "matched_markers": matched,
                "code_released": code_released,
                "quantitative_claims": falsifiable,
                "feasibility": feasibility,
                "threshold": threshold,
                "passes_gate": passes_gate,
            },
            notes=notes,
        )
        ctx.manifest.record_skill(result)
        return result


@register_skill("quant_scout", "reproducibility_triage")
def _make_triage_skill() -> ReproducibilityTriageSkill:
    return ReproducibilityTriageSkill()
