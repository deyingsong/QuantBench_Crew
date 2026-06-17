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
    relevance: RelevanceAssessment | None = None


@dataclass(frozen=True)
class EvidenceLink:
    """Pointer from an assertion to the artifact that supports it."""

    kind: str         # "artifact" | "paper_quote" | "metric" | "test"
    reference: str    # artifact path, manifest key, or citation
    detail: str = ""


@dataclass(frozen=True)
class ResearchCharter:
    """Configurable statement of what research is in scope for the scout."""

    purpose: str
    themes: tuple[str, ...] = ()
    must_have: tuple[str, ...] = ()      # e.g. "out-of-sample test", "net of costs"
    exclude: tuple[str, ...] = ()        # e.g. "pure theory", "no empirics"
    source_path: str = ""


@dataclass(frozen=True)
class RelevanceAssessment:
    """Charter-relative relevance for one candidate paper."""

    score: float                         # 0-1
    method: str                          # "embedding" | "charter_overlap"
    matched_themes: tuple[str, ...] = ()
    rationale: str = ""
    dimensions: dict[str, float] = field(default_factory=dict)
    signals: tuple[str, ...] = ()
    penalties: tuple[str, ...] = ()
    confidence: float = 0.0


@dataclass(frozen=True)
class RedFlag:
    """A detected quant-research pitfall, with the evidence for it."""

    kind: str        # "no_transaction_costs" | "in_sample_tuning"
                     # | "survivorship_prone" | "microcap_driven"
                     # | "short_sample" | "data_snooping"
    severity: str    # "info" | "warning" | "critical"
    rationale: str
    evidence: tuple[EvidenceLink, ...] = ()


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
class ResearchQuestionAssessment:
    """Research context and gap that motivate a paper."""

    question: str
    field_state: tuple[str, ...] = ()
    importance: tuple[str, ...] = ()
    existing_method_gap: tuple[str, ...] = ()
    claimed_contribution: tuple[str, ...] = ()
    confidence: float = 0.0
    evidence: tuple[EvidenceLink, ...] = ()


@dataclass(frozen=True)
class MethodologyAssessment:
    """Scientific method, mathematics, algorithms, and experiment settings."""

    summary: str
    equations: tuple[str, ...] = ()
    algorithms: tuple[str, ...] = ()
    experiment_settings: tuple[str, ...] = ()
    baselines: tuple[str, ...] = ()
    omitted_details: tuple[str, ...] = ()
    confidence: float = 0.0
    evidence: tuple[EvidenceLink, ...] = ()


@dataclass(frozen=True)
class EmpiricalSpecification:
    """Data, variables, splits, baselines, and metrics used by a paper."""

    datasets: tuple[str, ...] = ()
    features: tuple[str, ...] = ()
    labels: tuple[str, ...] = ()
    preprocessing: tuple[str, ...] = ()
    splits: tuple[str, ...] = ()
    baselines: tuple[str, ...] = ()
    metrics: tuple[str, ...] = ()
    confidence: float = 0.0
    evidence: tuple[EvidenceLink, ...] = ()


@dataclass(frozen=True)
class CritiqueAssessment:
    """Grounded criticism of a paper's assumptions, limits, and open work."""

    assumptions: tuple[str, ...] = ()
    author_stated_limitations: tuple[str, ...] = ()
    reader_inferred_threats: tuple[str, ...] = ()
    unanswered_questions: tuple[str, ...] = ()
    future_directions: tuple[str, ...] = ()
    confidence: float = 0.0
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
    relevance: RelevanceAssessment | None = None
    red_flags: tuple[RedFlag, ...] = ()
    question_assessment: ResearchQuestionAssessment | None = None
    methodology_assessment: MethodologyAssessment | None = None
    empirical_spec: EmpiricalSpecification | None = None
    critique: CritiqueAssessment | None = None


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
class SpanningResult:
    """Factor-spanning regression of candidate returns on a factor set."""

    factors: tuple[str, ...]             # e.g. ("MKT","SMB","HML","RMW","CMA","MOM")
    alpha: float                         # per-period intercept
    alpha_tstat: float
    betas: dict[str, float]
    r_squared: float
    residual_sharpe: float               # annualized, on regression residuals


@dataclass(frozen=True)
class DeflatedSharpe:
    """Bailey-Lopez de Prado deflated Sharpe ratio."""

    observed_sharpe: float
    n_trials: int                        # read from the run manifest
    deflated_sharpe: float
    p_value: float                       # P(true SR <= benchmark) under multiple testing
    haircut: float                       # observed - deflated


@dataclass(frozen=True)
class CapacityEstimate:
    """First-order capacity / liquidity sanity proxy."""

    average_turnover: float
    adv_participation: float             # share of ADV the strategy would consume
    capacity_usd: float | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RobustnessReport:
    """Subsample stability and parameter sensitivity for one strategy."""

    subsample_sharpes: dict[str, float]  # e.g. {"1965-1989": .., "1990-2014": ..}
    sign_stable: bool
    parameter_sensitivity: dict[str, float]  # param -> sharpe spread across sweep
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExperimentResult:
    """One declared Bench experiment with its configuration and verdict."""

    name: str
    dataset: str
    expect_edge: bool
    passed: bool
    configuration: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    baselines: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class StrategyEvaluation:
    """Multi-dataset comparison of one strategy against declared expectations."""

    paper: Paper
    experiments: tuple[ExperimentResult, ...]
    passed_all: bool
    pass_rate: float
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RobustnessAudit:
    """Auditable stress-test ledger and conservative robustness verdict."""

    experiments: tuple[ExperimentResult, ...]
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    unavailable_checks: tuple[str, ...]
    configuration_hash: str
    results_hash: str
    robust: bool
    recorded_experiments: int = 0
    disclosed_local_trials: int = 0
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvalCase:
    """One paper in the system's own regression suite."""

    slug: str
    paper: Paper
    data_tier: str                       # "french" | "crsp" | "synthetic"
    expected_outcome: str                # "reproduces" | "does_not_reproduce"
    targets: ReproductionTarget
    strategy: str = "momentum"           # named strategy the bench should run
    dataset: str = "planted_momentum"
    dataset_params: dict[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvalResult:
    """Outcome of running one EvalCase through the pipeline."""

    case: EvalCase
    achieved_verdict: str
    matches_expected: bool
    detail: str = ""


@dataclass(frozen=True)
class BenchmarkResult:
    """Benchmark metrics for a method or baseline."""

    paper: Paper
    dataset: str
    metrics: dict[str, float]
    baselines: dict[str, dict[str, float]] = field(default_factory=dict)
    notes: tuple[str, ...] = ()
    comparisons: tuple[ClaimComparison, ...] = ()
    spanning: SpanningResult | None = None
    deflated_sharpe: DeflatedSharpe | None = None
    capacity: CapacityEstimate | None = None
    strategy_evaluation: StrategyEvaluation | None = None
    robustness_audit: RobustnessAudit | None = None


@dataclass(frozen=True)
class RubricScore:
    """One scored dimension of the reviewer rubric."""

    dimension: str   # "reproducibility" | "robustness" | "net_of_cost_viability"
                     # | "novelty_vs_baselines" | "data_accessibility"
    score: int       # 0-4
    rationale: str
    evidence: tuple[EvidenceLink, ...] = ()


@dataclass(frozen=True)
class ClaimResultFinding:
    """One paper claim compared with the evidence produced by Bench."""

    metric: str
    claimed_value: float | None
    achieved_value: float | None
    tolerance: float | None
    status: str  # "reproduced" | "not_reproduced" | "not_evaluated"
    gap: float | None = None
    note: str = ""
    evidence: tuple[EvidenceLink, ...] = ()


@dataclass(frozen=True)
class ClaimsVsResultsAnalysis:
    """Forensic comparison of paper claims, results, and reproduction barriers."""

    findings: tuple[ClaimResultFinding, ...]
    implementation_issues: tuple[str, ...]
    reproducibility_issues: tuple[str, ...]
    reproduced_count: int
    failed_count: int
    unevaluated_count: int
    evidence: tuple[EvidenceLink, ...] = ()


@dataclass(frozen=True)
class ReportCompilation:
    """Evidence-linked final review assembled through expert diagnostic lenses."""

    executive_summary: str
    empirical_findings: tuple[str, ...]
    expert_lens_findings: tuple[str, ...]
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]
    open_questions: tuple[str, ...]
    markdown: str
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
    robustness: RobustnessReport | None = None
    claims_analysis: ClaimsVsResultsAnalysis | None = None
    compilation: ReportCompilation | None = None

    def to_markdown(self) -> str:
        """Render the review as a Markdown report."""

        if self.compilation is not None:
            return self.compilation.markdown
        from quantbench_crew.feedback import ensure_feedback_section

        return ensure_feedback_section(
            "\n".join(
                [
                    f"# {self.paper.title}",
                    "",
                    f"**Source:** {self.paper.source}",
                    _paper_link_line(self.paper),
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
            ),
            paper_slug=self.paper.slug,
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


def _paper_link_line(paper: Paper) -> str:
    url = paper.url or str(paper.raw.get("pdf_url") or "").strip()
    if not url:
        return "**Paper:** Not available from source metadata"
    return f"**Paper:** [Original paper]({url})"


def _rubric_table(rubric: tuple["RubricScore", ...]) -> str:
    if not rubric:
        return "No rubric scored (scaffold-only run)."

    rows = ["| Dimension | Score | Rationale | Evidence |", "| --- | ---: | --- | --- |"]
    for score in rubric:
        evidence = "; ".join(link.reference for link in score.evidence) or "—"
        rows.append(f"| {score.dimension} | {score.score}/4 | {score.rationale} | {evidence} |")
    return "\n".join(rows)
