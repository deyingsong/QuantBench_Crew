from quantbench_crew.agents import era
from quantbench_crew.agents.coder import QuantCoderAgent
from quantbench_crew.models import Paper, PaperAnalysis


def test_era_search_returns_best_solution() -> None:
    problem = era.Problem("maximize the numeric program")
    initial = era.Solution("0")

    candidates = iter((era.Solution("1"), era.Solution("3"), era.Solution("2")))

    def generate(
        problem: era.Problem,
        parent_solution: era.Solution,
        parent_score: float,
    ) -> era.Solution:
        del problem, parent_solution, parent_score
        return next(candidates)

    def execute(problem: era.Problem, solution: era.Solution) -> float:
        del problem
        return float(solution.program)

    solution, score = era.search(
        problem=problem,
        initial_solution=initial,
        initial_score=execute(problem, initial),
        generate_fn=generate,
        execute_fn=execute,
        num_iterations=3,
    )

    assert solution.program == "3"
    assert score == 3.0


def test_quant_coder_uses_era_plan_interface() -> None:
    analysis = PaperAnalysis(
        paper=Paper(
            title="Portfolio Forecasting with Transaction Costs",
            abstract="A machine learning method for portfolio return forecasting.",
        ),
        research_question="Can portfolio forecasts improve out-of-sample returns?",
        proposed_method="Machine learning forecasting method requiring validation.",
        assumptions=("transaction costs", "liquidity"),
        datasets=("returns",),
        metrics=("sharpe", "turnover"),
        limitations=("Metadata-only extraction; full PDF parsing is not connected yet.",),
    )

    plan = QuantCoderAgent().plan(analysis)

    assert plan.paper == analysis.paper
    assert any("benchmark_runner" in module for module in plan.modules)
    assert any("robustness" in module for module in plan.modules)
    assert any("sharpe" in test for test in plan.tests)
    assert "transaction costs" in " ".join(plan.open_questions).lower()
