from quantbench_crew.agents.scout import QuantScoutAgent
from quantbench_crew.models import Paper, ResearchCharter
from quantbench_crew.skills.scout.relevance_scorer import (
    RelevanceScorerSkill,
    assess_research_value,
)


def test_research_value_rewards_decision_useful_disclosures() -> None:
    strong = Paper(
        title="Out-of-sample momentum portfolios",
        abstract=(
            "We test cross-sectional momentum returns out-of-sample against a baseline "
            "using publicly available data and released code. Results are net of "
            "transaction costs with turnover, drawdown, liquidity, and robustness checks."
        ),
        authors=("A",),
        url="https://example.test/strong",
    )
    vague = Paper(title="A novel AI trading strategy", abstract="We propose a novel strategy.")
    charter = ResearchCharter(
        purpose="reproducible cross-sectional return predictability",
        themes=("momentum", "cross-sectional"),
        must_have=("returns",),
    )

    strong_score = assess_research_value(strong, charter)
    vague_score = assess_research_value(vague, charter)

    assert strong_score.score > vague_score.score
    assert strong_score.dimensions["empirical_evidence"] > vague_score.dimensions["empirical_evidence"]
    assert "net of costs" in strong_score.signals
    assert "insufficient abstract detail" in vague_score.penalties


def test_agent_uses_relevance_scorer_without_charter() -> None:
    scout = QuantScoutAgent(skills={"relevance_scorer": RelevanceScorerSkill()})
    scored = scout.rank(
        [Paper(title="Portfolio test", abstract="Out-of-sample robustness benchmark returns.")],
        max_papers=1,
    )[0]

    assert scored.relevance is not None
    assert scored.relevance.method == "research_value_rubric"
