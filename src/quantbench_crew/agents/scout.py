"""QuantScout agent for paper relevance scoring."""

from __future__ import annotations

from collections.abc import Iterable

from quantbench_crew.models import Paper, ScoredPaper


class QuantScoutAgent:
    """Rank candidate papers by keyword relevance."""

    def __init__(self, keywords: Iterable[str] | None = None) -> None:
        self.keywords = tuple(
            keyword.lower()
            for keyword in (
                keywords
                or (
                    "asset pricing",
                    "portfolio",
                    "market microstructure",
                    "forecasting",
                    "risk",
                    "machine learning",
                    "quantitative finance",
                )
            )
        )

    def rank(self, papers: Iterable[Paper], max_papers: int = 5) -> list[ScoredPaper]:
        scored = [self._score(paper) for paper in papers]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:max_papers]

    def _score(self, paper: Paper) -> ScoredPaper:
        text = f"{paper.title} {paper.abstract} {' '.join(paper.keywords)}".lower()
        reasons = tuple(keyword for keyword in self.keywords if keyword in text)
        title_bonus = sum(0.25 for keyword in self.keywords if keyword in paper.title.lower())
        score = len(reasons) + title_bonus
        return ScoredPaper(paper=paper, score=score, reasons=reasons)
