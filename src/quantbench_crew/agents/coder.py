"""ERA-backed QuantCoder agent for implementation planning."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from quantbench_crew.agents import era
from quantbench_crew.models import ImplementationPlan, PaperAnalysis
from quantbench_crew.skills.base import Skill


class QuantCoderAgent:
    """Use ERA-style search to create a conservative implementation plan."""

    def __init__(
        self,
        iterations: int = 3,
        c_puct: float = 1.0,
        skills: Mapping[str, Skill] | None = None,
    ) -> None:
        self.iterations = iterations
        self.c_puct = c_puct
        self.skills = dict(skills or {})

    def plan(self, analysis: PaperAnalysis) -> ImplementationPlan:
        problem = era.Problem(description=_problem_description(analysis))
        initial_plan = _initial_plan(analysis)
        initial_solution = _plan_to_solution(initial_plan)
        executor = _PlanExecutor(analysis)
        generator = _PlanGenerator(analysis)

        best_solution, _ = era.search(
            problem=problem,
            initial_solution=initial_solution,
            initial_score=executor(problem, initial_solution),
            generate_fn=generator,
            execute_fn=executor,
            num_iterations=self.iterations,
            c_puct=self.c_puct,
        )

        return _solution_to_plan(best_solution, analysis)


class _PlanGenerator:
    """Deterministic QuantBench generator compatible with ERA's interface."""

    def __init__(self, analysis: PaperAnalysis) -> None:
        self._candidates = (
            _data_first_plan(analysis),
            _method_first_plan(analysis),
            _robust_reproduction_plan(analysis),
        )
        self._index = 0

    def __call__(
        self,
        problem: era.Problem,
        parent_solution: era.Solution,
        parent_score: float,
    ) -> era.Solution:
        del problem, parent_solution, parent_score
        candidate = self._candidates[min(self._index, len(self._candidates) - 1)]
        self._index += 1
        return _plan_to_solution(candidate)


class _PlanExecutor:
    """Scores plan completeness without executing generated code."""

    def __init__(self, analysis: PaperAnalysis) -> None:
        self.analysis = analysis

    def __call__(self, problem: era.Problem, solution: era.Solution) -> float:
        del problem
        plan = _solution_to_plan(solution, self.analysis)
        text = " ".join(plan.modules + plan.tests + plan.open_questions).lower()
        score = 0.0
        score += 1.5 * len(plan.modules)
        score += 1.0 * len(plan.tests)
        score += 0.5 * len(plan.open_questions)
        score += _coverage_score(text, self.analysis.datasets, weight=1.5)
        score += _coverage_score(text, self.analysis.metrics, weight=1.5)
        score += _coverage_score(text, self.analysis.assumptions, weight=1.0)
        score += _keyword_bonus(text)
        return score


def _problem_description(analysis: PaperAnalysis) -> str:
    sections = {
        "research_question": analysis.research_question,
        "proposed_method": analysis.proposed_method,
        "datasets": analysis.datasets,
        "metrics": analysis.metrics,
        "assumptions": analysis.assumptions,
        "limitations": analysis.limitations,
    }
    return json.dumps(sections, sort_keys=True)


def _initial_plan(analysis: PaperAnalysis) -> ImplementationPlan:
    return ImplementationPlan(
        paper=analysis.paper,
        modules=(
            "datasets: load and validate benchmark inputs",
            "features: reproduce paper feature construction",
            "models: implement the proposed method behind a stable interface",
            "evaluation: compare method output against baselines",
        ),
        assumptions=analysis.assumptions,
        tests=(
            "unit tests for feature shapes and missing data handling",
            "unit tests for deterministic model output on toy data",
            "regression test for benchmark metric calculation",
        ),
        open_questions=(
            "Which exact train/test split did the paper use?",
            "Are transaction costs, turnover, and data availability constraints modeled?",
            "Does the method require proprietary data?",
        ),
    )


def _data_first_plan(analysis: PaperAnalysis) -> ImplementationPlan:
    dataset_note = _join_terms(analysis.datasets)
    return ImplementationPlan(
        paper=analysis.paper,
        modules=(
            f"data_contract: resolve source, point-in-time fields, and access for {dataset_note}",
            "dataset_loader: normalize dates, identifiers, returns, labels, and missing values",
            "feature_pipeline: recreate transformations with leakage checks and reproducible seeds",
            "baseline_suite: define naive, equal-weight, and paper-specific baselines",
        ),
        assumptions=analysis.assumptions,
        tests=(
            f"schema tests for required {dataset_note} columns and date ranges",
            "unit tests for point-in-time joins and missing data behavior",
            "fixture test proving feature generation is deterministic",
        ),
        open_questions=(
            "What raw data license and vendor fields are required?",
            "What is the paper's exact sample period and rebalancing frequency?",
            "How should unavailable or delisted assets be represented?",
        ),
    )


def _method_first_plan(analysis: PaperAnalysis) -> ImplementationPlan:
    metrics_note = _join_terms(analysis.metrics)
    return ImplementationPlan(
        paper=analysis.paper,
        modules=(
            "method_spec: translate the proposed method into typed training and inference APIs",
            "model_impl: implement the estimator with deterministic defaults and documented parameters",
            f"metric_impl: reproduce reported metrics including {metrics_note}",
            "experiment_runner: run baselines and candidate method under the same split protocol",
        ),
        assumptions=analysis.assumptions,
        tests=(
            "unit tests for estimator fit/predict behavior on toy data",
            f"metric tests for {metrics_note} against hand-calculated examples",
            "regression tests for benchmark ordering against baseline outputs",
        ),
        open_questions=(
            "Which hyperparameters are fixed by the paper versus tuned on validation data?",
            "What random seeds or cross-validation folds are required?",
            "Which baseline results must be reproduced before extending the method?",
        ),
    )


def _robust_reproduction_plan(analysis: PaperAnalysis) -> ImplementationPlan:
    dataset_note = _join_terms(analysis.datasets)
    metrics_note = _join_terms(analysis.metrics)
    assumption_note = _join_terms(analysis.assumptions)
    return ImplementationPlan(
        paper=analysis.paper,
        modules=(
            f"problem_spec: capture method, {dataset_note}, {metrics_note}, and known assumptions",
            "data_pipeline: build point-in-time dataset loading, validation, and feature generation",
            "method_adapter: expose fit, predict, and score methods for the reproduced model",
            "benchmark_runner: compare candidate, ablations, and baselines on identical splits",
            "robustness_checks: evaluate transaction costs, turnover, missing data, and sensitivity",
        ),
        assumptions=analysis.assumptions,
        tests=(
            "contract tests for dataset schema, date alignment, and leakage prevention",
            "unit tests for model determinism, parameter validation, and edge-case inputs",
            f"metric tests for {metrics_note} using hand-computed fixtures",
            "integration test that runs a tiny end-to-end benchmark with baseline comparison",
            f"robustness tests covering assumption changes: {assumption_note}",
        ),
        open_questions=(
            "Which exact train/test split, validation rule, and sample period did the paper use?",
            "Are transaction costs, turnover, liquidity, and data availability constraints modeled?",
            "Does the method require proprietary data or unreleased preprocessing steps?",
            "Which reported table or figure is the first reproduction target?",
        ),
    )


def _plan_to_solution(plan: ImplementationPlan) -> era.Solution:
    payload = {
        "modules": plan.modules,
        "assumptions": plan.assumptions,
        "tests": plan.tests,
        "open_questions": plan.open_questions,
    }
    return era.Solution(json.dumps(payload, sort_keys=True))


def _solution_to_plan(solution: era.Solution, analysis: PaperAnalysis) -> ImplementationPlan:
    payload = _load_solution_payload(solution)
    return ImplementationPlan(
        paper=analysis.paper,
        modules=_string_tuple(payload.get("modules")),
        assumptions=_string_tuple(payload.get("assumptions")) or analysis.assumptions,
        tests=_string_tuple(payload.get("tests")),
        open_questions=_string_tuple(payload.get("open_questions")),
    )


def _load_solution_payload(solution: era.Solution) -> dict[str, Any]:
    try:
        payload = json.loads(solution.program)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def _coverage_score(text: str, terms: tuple[str, ...], weight: float) -> float:
    return sum(weight for term in terms if _is_specific_term(term) and term.lower() in text)


def _keyword_bonus(text: str) -> float:
    keywords = (
        "baseline",
        "deterministic",
        "integration",
        "leakage",
        "point-in-time",
        "robustness",
        "transaction costs",
    )
    return sum(0.75 for keyword in keywords if keyword in text)


def _join_terms(terms: tuple[str, ...]) -> str:
    specific = tuple(term for term in terms if _is_specific_term(term))
    return ", ".join(specific) if specific else "paper-identified requirements"


def _is_specific_term(term: str) -> bool:
    generic_fragments = (
        "not identified",
        "requires human review",
        "metadata-only",
    )
    lowered = term.lower()
    return bool(term.strip()) and not any(fragment in lowered for fragment in generic_fragments)

