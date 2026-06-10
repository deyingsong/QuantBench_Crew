from pathlib import Path

import pytest

from quantbench_crew.models import Paper
from quantbench_crew.skills.scout.triage import ReproducibilityTriageSkill
from quantbench_crew.tools.arxiv_tool import load_local_papers, sample_papers

GOLDEN = load_local_papers(Path(__file__).parent / "fixtures" / "golden_paper.json")[0]


def _threshold_config(threshold: float) -> dict:
    return {
        "agents": {
            "quant_scout": {
                "skills": {"reproducibility_triage": {"enabled": True, "threshold": threshold}}
            }
        }
    }


def test_golden_paper_is_public_with_code_and_passes(make_ctx) -> None:
    ctx = make_ctx()
    result = ReproducibilityTriageSkill().run(ctx, paper=GOLDEN)

    assert result.status == "ok"
    payload = result.payload
    assert payload["data_tier"] == "public"
    assert payload["code_released"] is True
    assert payload["quantitative_claims"] is True
    assert payload["feasibility"] == pytest.approx(1.0)
    assert payload["passes_gate"] is True
    # The triage decision is part of the trial record.
    assert ctx.manifest.skill_results[0].skill == "reproducibility_triage"


def test_vendor_paper_is_gated_at_default_threshold(make_ctx) -> None:
    vendor_paper = sample_papers()[0]  # mentions CRSP-like monthly data

    result = ReproducibilityTriageSkill().run(make_ctx(), paper=vendor_paper)

    assert result.payload["data_tier"] == "vendor"
    assert result.payload["feasibility"] == pytest.approx(0.4)
    assert result.payload["passes_gate"] is False


def test_proprietary_paper_scores_lowest(make_ctx) -> None:
    paper = Paper(
        title="Alpha from Internal Order Flow",
        abstract="We use proprietary internal data from an order-level data feed.",
    )

    result = ReproducibilityTriageSkill().run(make_ctx(), paper=paper)

    assert result.payload["data_tier"] == "proprietary"
    assert result.payload["feasibility"] == pytest.approx(0.1)


def test_unmarked_paper_is_unknown_tier(make_ctx) -> None:
    paper = Paper(title="A Study of Returns", abstract="We study returns.")

    result = ReproducibilityTriageSkill().run(make_ctx(), paper=paper)

    assert result.payload["data_tier"] == "unknown"
    assert result.payload["feasibility"] == pytest.approx(0.6)


def test_threshold_is_configurable(make_ctx) -> None:
    vendor_paper = sample_papers()[0]

    lenient = ReproducibilityTriageSkill().run(
        make_ctx(config=_threshold_config(0.3)), paper=vendor_paper
    )
    strict = ReproducibilityTriageSkill().run(
        make_ctx(config=_threshold_config(0.9)), paper=vendor_paper
    )

    assert lenient.payload["passes_gate"] is True
    assert strict.payload["passes_gate"] is False
