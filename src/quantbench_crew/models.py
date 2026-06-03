"""Core domain models for the QuantBench Crew workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class Paper:
    """Metadata and available text for a research paper."""

    title: str
    abstract: str
    authors: tuple[str, ...] = ()
    source: str = "local"
    url: str | None = None
    published: date | None = None
    keywords: tuple[str, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def slug(self) -> str:
        words = "".join(ch.lower() if ch.isalnum() else "-" for ch in self.title)
        return "-".join(part for part in words.split("-") if part)[:80] or "paper"


@dataclass(frozen=True)
class ScoredPaper:
    """A paper with a relevance score from the scout agent."""

    paper: Paper
    score: float
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaperAnalysis:
    """Structured analysis extracted from a paper."""

    paper: Paper
    research_question: str
    proposed_method: str
    assumptions: tuple[str, ...]
    datasets: tuple[str, ...]
    metrics: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ImplementationPlan:
    """Plan for implementing a paper method."""

    paper: Paper
    modules: tuple[str, ...]
    assumptions: tuple[str, ...]
    tests: tuple[str, ...]
    open_questions: tuple[str, ...]


@dataclass(frozen=True)
class BenchmarkResult:
    """Benchmark metrics for a method or baseline."""

    paper: Paper
    dataset: str
    metrics: dict[str, float]
    baselines: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewReport:
    """Final research review for a paper."""

    paper: Paper
    analysis: PaperAnalysis
    implementation_plan: ImplementationPlan
    benchmark_result: BenchmarkResult
    verdict: str
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]
    open_questions: tuple[str, ...]

    def to_markdown(self) -> str:
        """Render the review as a Markdown report."""

        return "\n".join(
            [
                f"# {self.paper.title}",
                "",
                f"**Source:** {self.paper.source}",
                f"**Verdict:** {self.verdict}",
                "",
                "## Research Question",
                self.analysis.research_question,
                "",
                "## Proposed Method",
                self.analysis.proposed_method,
                "",
                "## Implementation Plan",
                _bullet_list(self.implementation_plan.modules),
                "",
                "## Benchmark Metrics",
                _metric_table(self.benchmark_result.metrics),
                "",
                "## Strengths",
                _bullet_list(self.strengths),
                "",
                "## Weaknesses",
                _bullet_list(self.weaknesses),
                "",
                "## Open Questions",
                _bullet_list(self.open_questions),
                "",
                "## Disclaimer",
                "This report supports research review only and is not financial advice.",
                "",
            ]
        )


def _bullet_list(items: tuple[str, ...]) -> str:
    if not items:
        return "- None identified."
    return "\n".join(f"- {item}" for item in items)


def _metric_table(metrics: dict[str, float]) -> str:
    if not metrics:
        return "No benchmark metrics available."

    rows = ["| Metric | Value |", "| --- | ---: |"]
    rows.extend(f"| {name} | {value:.4f} |" for name, value in metrics.items())
    return "\n".join(rows)
