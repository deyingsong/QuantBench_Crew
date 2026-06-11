"""QB-18 acceptance: charter relevance is recorded and re-ranks sensibly."""

from quantbench_crew.agents.scout import QuantScoutAgent
from quantbench_crew.models import Paper, ResearchCharter
from quantbench_crew.skills.scout.charter_relevance import (
    CharterRelevanceSkill,
    assess_relevance,
    load_charter,
)

CHARTER = ResearchCharter(
    purpose="Cross-sectional momentum and value with out-of-sample tests",
    themes=("momentum", "value", "cross-section"),
    must_have=("returns",),
    exclude=("pure theory",),
)


def test_assess_relevance_rewards_on_charter_paper() -> None:
    on = Paper(
        title="Cross-sectional momentum and value in equity returns",
        abstract="We study momentum and value returns in the cross-section.",
    )
    off = Paper(
        title="A general equilibrium model of asset prices",
        abstract="A pure theory treatment with no empirical returns.",
    )

    on_score = assess_relevance(on, CHARTER)
    off_score = assess_relevance(off, CHARTER)

    assert on_score.method == "charter_overlap"
    assert on_score.score > off_score.score
    assert "momentum" in on_score.matched_themes and "value" in on_score.matched_themes


def test_exclusion_penalizes_score() -> None:
    paper = Paper(
        title="Momentum returns",
        abstract="Momentum and value cross-section returns, a pure theory note.",
    )
    excluded = assess_relevance(paper, CHARTER)
    assert "pure theory" in excluded.rationale
    # Halved by the exclusion despite strong theme overlap.
    assert excluded.score < 0.6


def test_charter_reorders_ranking_above_keyword_score() -> None:
    # Keyword-dense but off-charter vs keyword-sparse but on-charter.
    keyword_heavy = Paper(
        title="Risk, forecasting, portfolio and market microstructure",
        abstract="risk forecasting portfolio market microstructure machine learning",
        keywords=("risk", "forecasting", "portfolio"),
    )
    on_charter = Paper(
        title="Cross-sectional momentum and value returns",
        abstract="momentum value cross-section returns",
    )

    no_charter = QuantScoutAgent()
    plain = no_charter.rank([keyword_heavy, on_charter], max_papers=2)
    assert plain[0].paper.title.startswith("Risk")  # keyword score wins

    with_charter = QuantScoutAgent(
        skills={"charter_relevance": CharterRelevanceSkill()},
        charter=CHARTER,
    )
    reranked = with_charter.rank([keyword_heavy, on_charter], max_papers=2)
    assert reranked[0].paper.title.startswith("Cross-sectional")  # charter wins
    assert reranked[0].relevance is not None
    assert reranked[0].relevance.score > reranked[1].relevance.score


def test_record_relevance_writes_manifest_entry(make_ctx) -> None:
    scout = QuantScoutAgent(
        skills={"charter_relevance": CharterRelevanceSkill()}, charter=CHARTER
    )
    scored = scout.rank(
        [Paper(title="Momentum returns", abstract="momentum value returns")], max_papers=1
    )[0]
    ctx = make_ctx()

    result = scout.record_relevance(scored, ctx)

    assert result is not None
    assert result.payload["method"] == "charter_overlap"
    assert ctx.manifest.skill_results[-1].skill == "charter_relevance"


def test_no_charter_means_no_relevance_and_phase1_ranking() -> None:
    scout = QuantScoutAgent(skills={"charter_relevance": CharterRelevanceSkill()})
    scored = scout.rank([Paper(title="Momentum", abstract="returns")], max_papers=1)[0]
    assert scored.relevance is None  # charter absent => Phase 1 behavior


def test_load_charter_from_config() -> None:
    config = {"agents": {"quant_scout": {"charter": {"purpose": "p", "themes": ["momentum"]}}}}
    charter = load_charter(config)
    assert charter is not None
    assert charter.themes == ("momentum",)
    assert load_charter({"agents": {"quant_scout": {}}}) is None
