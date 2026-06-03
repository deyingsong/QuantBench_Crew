"""QuantCoder agent for implementation planning."""

from __future__ import annotations

from quantbench_crew.models import ImplementationPlan, PaperAnalysis


class QuantCoderAgent:
    """Create a conservative implementation plan from a paper analysis."""

    def plan(self, analysis: PaperAnalysis) -> ImplementationPlan:
        modules = (
            "datasets: load and validate benchmark inputs",
            "features: reproduce paper feature construction",
            "models: implement the proposed method behind a stable interface",
            "evaluation: compare method output against baselines",
        )
        tests = (
            "unit tests for feature shapes and missing data handling",
            "unit tests for deterministic model output on toy data",
            "regression test for benchmark metric calculation",
        )
        open_questions = tuple(
            item
            for item in (
                "Which exact train/test split did the paper use?",
                "Are transaction costs, turnover, and data availability constraints modeled?",
                "Does the method require proprietary data?",
            )
            if item
        )
        return ImplementationPlan(
            paper=analysis.paper,
            modules=modules,
            assumptions=analysis.assumptions,
            tests=tests,
            open_questions=open_questions,
        )
