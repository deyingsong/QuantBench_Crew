"""QuantReviewer agent for final synthesis."""

from __future__ import annotations

from collections.abc import Mapping

from quantbench_crew.models import (
    BenchmarkResult,
    ImplementationPlan,
    PaperAnalysis,
    ReviewReport,
)
from quantbench_crew.skills.base import RunContext, Skill


class QuantReviewerAgent:
    """Synthesize paper analysis, implementation notes, and benchmark metrics."""

    def __init__(self, skills: Mapping[str, Skill] | None = None) -> None:
        self.skills = dict(skills or {})

    def review(
        self,
        analysis: PaperAnalysis,
        implementation_plan: ImplementationPlan,
        benchmark_result: BenchmarkResult,
        ctx: RunContext | None = None,
    ) -> ReviewReport:
        open_questions = tuple(
            dict.fromkeys(
                implementation_plan.open_questions
                + analysis.limitations
                + benchmark_result.notes
            )
        )

        if ctx is not None and "rubric_verdict" in self.skills:
            return self._review_with_rubric(
                analysis, implementation_plan, benchmark_result, open_questions, ctx
            )

        return self._review_static(
            analysis, implementation_plan, benchmark_result, open_questions
        )

    def _review_with_rubric(
        self,
        analysis: PaperAnalysis,
        implementation_plan: ImplementationPlan,
        benchmark_result: BenchmarkResult,
        open_questions: tuple[str, ...],
        ctx: RunContext,
    ) -> ReviewReport:
        from quantbench_crew.benchmarks.robustness import robustness_from_dict
        from quantbench_crew.skills.reviewer.rubric import build_rubric

        result = self.skills["rubric_verdict"].run(
            ctx, analysis=analysis, benchmark_result=benchmark_result
        )
        payload = result.payload

        # The robustness report lives in the walk-forward payload; surface it
        # on the report so the markdown and downstream consumers can read it.
        robustness = None
        for skill_result in reversed(ctx.manifest.skill_results):
            if skill_result.skill == "walk_forward":
                robustness = robustness_from_dict(skill_result.payload.get("robustness"))
                break

        return ReviewReport(
            paper=analysis.paper,
            analysis=analysis,
            implementation_plan=implementation_plan,
            benchmark_result=benchmark_result,
            verdict=payload["verdict"],
            strengths=tuple(payload["strengths"]),
            weaknesses=tuple(payload["weaknesses"]),
            open_questions=open_questions,
            rubric=build_rubric(payload),
            robustness=robustness,
        )

    def _review_static(
        self,
        analysis: PaperAnalysis,
        implementation_plan: ImplementationPlan,
        benchmark_result: BenchmarkResult,
        open_questions: tuple[str, ...],
    ) -> ReviewReport:
        # No rubric skill: the benchmark is the placeholder series, so an
        # upbeat verdict would be backed by fake returns. Say scaffold-only.
        placeholder = any("placeholder" in note.lower() for note in benchmark_result.notes)
        verdict = "scaffold-only" if placeholder else "inconclusive"
        strengths = (
            "Paper is relevant to the configured quantitative research scope.",
            "Workflow produced traceable analysis, implementation, and benchmark artifacts.",
        )
        weaknesses = (
            "Current analysis is based on metadata rather than full paper parsing.",
            "Benchmark result uses placeholder returns and is not evidence of practical value.",
        )
        return ReviewReport(
            paper=analysis.paper,
            analysis=analysis,
            implementation_plan=implementation_plan,
            benchmark_result=benchmark_result,
            verdict=verdict,
            strengths=strengths,
            weaknesses=weaknesses,
            open_questions=open_questions,
        )
