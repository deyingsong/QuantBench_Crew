"""QuantReviewer agent for final synthesis."""

from __future__ import annotations

from quantbench_crew.models import BenchmarkResult, ImplementationPlan, PaperAnalysis, ReviewReport


class QuantReviewerAgent:
    """Synthesize paper analysis, implementation notes, and benchmark metrics."""

    def review(
        self,
        analysis: PaperAnalysis,
        implementation_plan: ImplementationPlan,
        benchmark_result: BenchmarkResult,
    ) -> ReviewReport:
        sharpe = benchmark_result.metrics.get("sharpe", 0.0)
        verdict = "promising" if sharpe > 0.5 else "inconclusive"
        strengths = (
            "Paper is relevant to the configured quantitative research scope.",
            "Workflow produced traceable analysis, implementation, and benchmark artifacts.",
        )
        weaknesses = (
            "Current analysis is based on metadata rather than full paper parsing.",
            "Benchmark result uses placeholder returns and is not evidence of practical value.",
        )
        open_questions = tuple(
            dict.fromkeys(
                implementation_plan.open_questions
                + analysis.limitations
                + benchmark_result.notes
            )
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
