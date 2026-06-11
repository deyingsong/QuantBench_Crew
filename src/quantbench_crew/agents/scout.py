"""QuantScout agent for paper relevance scoring."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace

from quantbench_crew.models import Paper, RelevanceAssessment, ResearchCharter, ScoredPaper
from quantbench_crew.skills.base import RunContext, Skill, SkillResult


class QuantScoutAgent:
    """Rank candidate papers by keyword and (optional) charter relevance."""

    def __init__(
        self,
        keywords: Iterable[str] | None = None,
        skills: Mapping[str, Skill] | None = None,
        charter: ResearchCharter | None = None,
        relevance_boost: float = 10.0,
    ) -> None:
        self.skills = dict(skills or {})
        self.charter = charter
        self.relevance_boost = relevance_boost
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

    def record_relevance(
        self, scored: ScoredPaper, ctx: "RunContext | None"
    ) -> "SkillResult | None":
        """Record the charter-relevance assessment for a ranked paper."""

        skill = self.skills.get("charter_relevance")
        if skill is None or ctx is None or scored.relevance is None:
            return None
        return skill.run(ctx, paper=scored.paper, relevance=scored.relevance)

    def _score(self, paper: Paper) -> ScoredPaper:
        text = f"{paper.title} {paper.abstract} {' '.join(paper.keywords)}".lower()
        reasons = tuple(keyword for keyword in self.keywords if keyword in text)
        title_bonus = sum(0.25 for keyword in self.keywords if keyword in paper.title.lower())
        score = len(reasons) + title_bonus

        relevance = self._relevance(paper)
        if relevance is not None:
            # Charter relevance is the dominant ranking signal when enabled;
            # the keyword score breaks ties among similarly-relevant papers.
            score += relevance.score * self.relevance_boost
        return ScoredPaper(paper=paper, score=score, reasons=reasons, relevance=relevance)

    def _relevance(self, paper: Paper) -> RelevanceAssessment | None:
        if self.charter is None or "charter_relevance" not in self.skills:
            return None
        from quantbench_crew.skills.scout.charter_relevance import assess_relevance

        return assess_relevance(paper, self.charter)
