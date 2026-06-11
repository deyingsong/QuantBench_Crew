"""Core domain models for the QuantBench Crew workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
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
class EvidenceLink:
    """Pointer from an assertion to the artifact that supports it."""

    kind: str         # "artifact" | "paper_quote" | "metric" | "test"
    reference: str    # artifact path, manifest key, or citation
    detail: str = ""


@dataclass(frozen=True)
class Claim:
    """A falsifiable quantitative claim made by the paper."""

    metric: str            # canonical metric name, e.g. "sharpe"
    value: float
    unit: str = ""         # e.g. "annualized", "monthly", "%"
    context: str = ""      # e.g. "long-short decile portfolio, net of costs"
    tolerance: float = 0.2 # relative tolerance band for reproduction
    source: str = ""       # e.g. "Table 3, Panel A"


@dataclass(frozen=True)
class ReproductionTarget:
    """The headline result the pipeline tries to reproduce."""

    paper: Paper
    claims: tuple[Claim, ...]
    table_reference: str = ""
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClaimComparison:
    """Achieved metric versus the paper's claimed value."""

    claim: Claim
    achieved: float
    within_tolerance: bool
    note: str = ""


@dataclass(frozen=True)
class MethodSpec:
    """Implementable specification extracted from a paper.

    This is the coder's real input; the free-text proposed_method field is
    not implementable on its own.
    """

    paper: Paper
    universe: str                  # e.g. "US common stocks, price > $5"
    frequency: str                 # "daily" | "weekly" | "monthly"
    signal_definition: str         # formula or pseudocode for the signal
    portfolio_construction: str    # e.g. "decile long-short, value-weighted"
    rebalance_frequency: str       # e.g. "monthly"
    holding_period: str            # e.g. "1 month, overlapping"
    sample_start: date | None = None
    sample_end: date | None = None
    evaluation_protocol: str = ""  # split rules, validation scheme
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    data_requirements: tuple[str, ...] = ()
    extraction_confidence: float = 0.0   # 0-1 extractor self-assessment
    evidence: tuple[EvidenceLink, ...] = ()


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
    method_spec: MethodSpec | None = None
    reproduction_target: ReproductionTarget | None = None


@dataclass(frozen=True)
class ImplementationPlan:
    """Plan for implementing a paper method."""

    paper: Paper
    modules: tuple[str, ...]
    assumptions: tuple[str, ...]
    tests: tuple[str, ...]
    open_questions: tuple[str, ...]


@dataclass(frozen=True)
class StrategyArtifact:
    """Generated implementation produced by the coder."""

    paper: Paper
    code_path: Path                # module implementing the Strategy contract
    entry_point: str               # e.g. "build_strategy"
    test_paths: tuple[Path, ...] = ()
    plan: ImplementationPlan | None = None
    generation_manifest: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BenchmarkResult:
    """Benchmark metrics for a method or baseline."""

    paper: Paper
    dataset: str
    metrics: dict[str, float]
    baselines: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: tuple[str, ...] = ()
    comparisons: tuple[ClaimComparison, ...] = ()


@dataclass(frozen=True)
class RubricScore:
    """One scored dimension of the reviewer rubric."""

    dimension: str   # "reproducibility" | "robustness" | "net_of_cost_viability"
                     # | "novelty_vs_baselines" | "data_accessibility"
    score: int       # 0-4
    rationale: str
    evidence: tuple[EvidenceLink, ...] = ()


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
    rubric: tuple[RubricScore, ...] = ()

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
                "## Rubric",
                _rubric_table(self.rubric),
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


def _rubric_table(rubric: tuple["RubricScore", ...]) -> str:
    if not rubric:
        return "No rubric scored (scaffold-only run)."

    rows = ["| Dimension | Score | Rationale | Evidence |", "| --- | ---: | --- | --- |"]
    for score in rubric:
        evidence = "; ".join(link.reference for link in score.evidence) or "—"
        rows.append(f"| {score.dimension} | {score.score}/4 | {score.rationale} | {evidence} |")
    return "\n".join(rows)
