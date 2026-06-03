"""ERA-compatible Flat UCB Tree Search primitives.

This module mirrors the public Google Research ERA reference interface
(https://github.com/google-research/era) while keeping the QuantBench workflow
self-contained and deterministic for local tests.
"""

from __future__ import annotations

import dataclasses
import math
from typing import Optional, Protocol


@dataclasses.dataclass(frozen=True)
class Problem:
    """Object that defines the problem to be solved."""

    description: str


@dataclasses.dataclass(frozen=True)
class Solution:
    """Object that defines a candidate solution to the problem."""

    program: str


@dataclasses.dataclass
class Node:
    """Node in the Flat UCB search tree."""

    index: int
    parent_index: Optional[int]
    solution: Solution
    score: float
    num_visits: int = 0
    rank_score: float = 0.5
    puct: float = 0.5


class Generate(Protocol):
    """Generates a new solution based on the parent solution."""

    def __call__(
        self,
        problem: Problem,
        parent_solution: Solution,
        parent_score: float,
    ) -> Solution:
        ...


class Execute(Protocol):
    """Scores a solution in the context of a problem."""

    def __call__(self, problem: Problem, solution: Solution) -> float:
        ...


def search(
    problem: Problem,
    initial_solution: Solution,
    initial_score: float,
    generate_fn: Generate,
    execute_fn: Execute,
    num_iterations: int,
    c_puct: float = 1.0,
) -> tuple[Solution, float]:
    """Perform Flat UCB tree search and return the best solution found."""

    if num_iterations < 0:
        raise ValueError("num_iterations must be non-negative")

    nodes = [
        Node(
            index=0,
            parent_index=None,
            solution=initial_solution,
            score=initial_score,
        )
    ]

    for _ in range(num_iterations):
        _compute_rank_scores(nodes)
        _compute_pucts(nodes, c_puct)
        parent = max(nodes, key=lambda node: node.puct)
        solution = generate_fn(problem, parent.solution, parent.score)
        score = execute_fn(problem, solution)
        child = Node(
            index=len(nodes),
            parent_index=parent.index,
            solution=solution,
            score=score,
        )
        nodes.append(child)
        _backpropagate_visit(nodes, child)

    best = max(nodes, key=lambda node: node.score)
    return best.solution, best.score


def _compute_rank_scores(nodes: list[Node]) -> None:
    if len(nodes) == 1:
        nodes[0].rank_score = 0.5
        return

    ranked = sorted(nodes, key=lambda node: node.score)
    denominator = len(ranked) - 1
    for rank, node in enumerate(ranked):
        node.rank_score = rank / denominator


def _compute_pucts(nodes: list[Node], c_puct: float) -> None:
    prior = 1 / len(nodes)
    total_visits = sum(node.num_visits for node in nodes)
    exploration = math.sqrt(total_visits)
    for node in nodes:
        node.puct = node.rank_score + c_puct * prior * exploration / (1 + node.num_visits)


def _backpropagate_visit(nodes: list[Node], node: Node) -> None:
    node.num_visits += 1
    if node.parent_index is not None:
        _backpropagate_visit(nodes, nodes[node.parent_index])
