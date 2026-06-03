from pathlib import Path

from quantbench_crew.agents.reader import QuantReaderAgent, document_paths_for_paper
from quantbench_crew.models import Paper


class FakePaperQAClient:
    def analyze(self, paper: Paper) -> str:
        assert paper.title == "Machine Learning for Asset Pricing"
        return """
        {
          "research_question": "Can machine learning forecasts improve portfolio returns?",
          "proposed_method": "A supervised forecasting model with portfolio rebalancing.",
          "assumptions": ["transaction costs are modeled", "liquidity screens are used"],
          "datasets": ["CRSP monthly returns"],
          "metrics": ["Sharpe", "turnover", "drawdown"],
          "limitations": ["Needs full replication data access"]
        }
        """


def test_reader_uses_paperqa_client_output() -> None:
    paper = Paper(
        title="Machine Learning for Asset Pricing",
        abstract="Metadata is intentionally sparse.",
    )

    analysis = QuantReaderAgent(paperqa_client=FakePaperQAClient()).analyze(paper)

    assert analysis.research_question == "Can machine learning forecasts improve portfolio returns?"
    assert analysis.datasets == ("CRSP monthly returns",)
    assert analysis.metrics == ("Sharpe", "turnover", "drawdown")
    assert analysis.limitations == ("Needs full replication data access",)


def test_reader_falls_back_to_metadata_without_paperqa() -> None:
    paper = Paper(
        title="Liquidity Risk and Intraday Market Microstructure",
        abstract="This paper evaluates liquidity risk using intraday returns.",
    )

    analysis = QuantReaderAgent(use_paperqa=False).analyze(paper)

    assert analysis.datasets == ("intraday", "returns")
    assert analysis.proposed_method.startswith("Risk modeling method")
    assert analysis.limitations == (
        "Metadata-only extraction; PaperQA2 document analysis was not available.",
    )


def test_document_paths_for_paper_reads_supported_raw_keys(tmp_path: Path) -> None:
    paper_path = tmp_path / "paper.txt"
    paper_path.write_text("sample paper text", encoding="utf-8")
    missing_path = tmp_path / "missing.pdf"
    paper = Paper(
        title="Local Paper",
        abstract="",
        raw={"document_paths": [str(paper_path), str(missing_path)]},
    )

    assert document_paths_for_paper(paper) == (paper_path,)
