"""QuantScout agent for paper relevance scoring."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from quantbench_crew.models import Paper, ScoredPaper
from quantbench_crew.skills.base import RunContext, Skill, SkillResult


class QuantScoutAgent:
    """Rank candidate papers by keyword relevance."""

    def __init__(
        self,
        keywords: Iterable[str] | None = None,
        skills: Mapping[str, Skill] | None = None,
    ) -> None:
        self.skills = dict(skills or {})
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

    def triage(self, scored: ScoredPaper, ctx: "RunContext | None") -> "SkillResult | None":
        """Run the reproducibility triage skill for one ranked paper.

        Returns None when the skill is not enabled or no run context exists;
        the workflow then proceeds ungated, exactly as before skills existed.
        """

        skill = self.skills.get("reproducibility_triage")
        if skill is None or ctx is None:
            return None
        return skill.run(ctx, paper=scored.paper)

    def _score(self, paper: Paper) -> ScoredPaper:
        text = f"{paper.title} {paper.abstract} {' '.join(paper.keywords)}".lower()
        reasons = tuple(keyword for keyword in self.keywords if keyword in text)
        title_bonus = sum(0.25 for keyword in self.keywords if keyword in paper.title.lower())
        score = len(reasons) + title_bonus
        return ScoredPaper(paper=paper, score=score, reasons=reasons)
