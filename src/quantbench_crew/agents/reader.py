"""QuantReader agent for deterministic first-pass paper extraction."""

from __future__ import annotations

from quantbench_crew.models import Paper, PaperAnalysis
from quantbench_crew.tools.paper_parser import keyword_extract, sentence_summary


class QuantReaderAgent:
    """Extract structured method notes from a paper record."""

    def analyze(self, paper: Paper) -> PaperAnalysis:
        text = f"{paper.title}. {paper.abstract}"
        datasets = keyword_extract(
            text,
            candidates=("crsp", "compustat", "wrds", "optionmetrics", "intraday", "returns"),
        )
        metrics = keyword_extract(
            text,
            candidates=("sharpe", "accuracy", "rmse", "drawdown", "turnover", "return"),
        )
        assumptions = keyword_extract(
            text,
            candidates=("stationary", "linear", "transaction costs", "liquidity", "no arbitrage"),
        )

        return PaperAnalysis(
            paper=paper,
            research_question=sentence_summary(
                paper.abstract,
                fallback="Identify whether the paper proposes a testable quantitative finance method.",
            ),
            proposed_method=_method_hint(text),
            assumptions=assumptions or ("Requires human review of modeling assumptions.",),
            datasets=datasets or ("Dataset not identified from metadata.",),
            metrics=metrics or ("Evaluation metrics not identified from metadata.",),
            limitations=("Metadata-only extraction; full PDF parsing is not connected yet.",),
        )


def _method_hint(text: str) -> str:
    lowered = text.lower()
    if "machine learning" in lowered or "neural" in lowered:
        return "Machine learning method requiring model specification and validation protocol review."
    if "portfolio" in lowered:
        return "Portfolio construction or allocation method requiring benchmark comparison."
    if "risk" in lowered:
        return "Risk modeling method requiring stress and robustness evaluation."
    if "forecast" in lowered or "predict" in lowered:
        return "Forecasting method requiring out-of-sample evaluation."
    return "Method details require full-text extraction before implementation."
