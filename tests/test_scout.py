from quantbench_crew.agents.scout import QuantScoutAgent
from quantbench_crew.models import Paper


def test_scout_ranks_relevant_paper_first() -> None:
    scout = QuantScoutAgent(keywords=("asset pricing", "portfolio"))
    relevant = Paper(
        title="Asset Pricing and Portfolio Benchmarks",
        abstract="A benchmark study.",
    )
    irrelevant = Paper(
        title="Corporate Disclosure Narratives",
        abstract="A text analysis study.",
    )

    ranked = scout.rank([irrelevant, relevant], max_papers=2)

    assert ranked[0].paper == relevant
    assert ranked[0].score > ranked[1].score
