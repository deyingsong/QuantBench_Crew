# Skills Design Note

Status: proposed
Date: 2026-06-10
Scope: extend the existing five-agent skeleton with per-agent skills, without changing agent public APIs or the frozen dataclass discipline.

## Motivation

The current pipeline is a deterministic walking skeleton. Two structural gaps
keep it from doing real work:

1. The coder produces a text plan, not executable code, so the bench agent has
   nothing to run and currently ignores its input.
2. Agent outputs are not tied to evidence, so the reviewer emits the same
   verdict text for every paper.

This note defines a skill plug-in model, the new domain dataclasses, the
per-agent skill roadmap, and the Phase 1 ticket breakdown. The organizing
conviction: the pipeline's value lives in the Coder -> Bench seam (turning
extracted methods into executable, scored artifacts), and every skill either
feeds that seam or audits its output.

## Guiding Principles

1. **Vertical slice before horizontal polish.** One paper through a fully real
   pipeline before any single agent gets clever.
2. **Skills are plug-ins, agents are orchestrators.** Agent public APIs
   (`rank`, `analyze`, `plan`, `evaluate`, `review`) and existing dataclasses
   stay. Every skill keeps a deterministic offline fallback so the dry
   workflow always runs.
3. **Evidence-linked outputs.** An agent may only assert what it can point to
   an artifact for.
4. **Validate the harness on synthetic truth first.** Run the machine on
   synthetic markets with planted effects and pure noise before real papers.
   If the system does not flag noise as noise, nothing downstream is
   trustworthy.

## Skill Plumbing

A skill is a named, registered, per-agent capability with a typed result and
an availability check (credentials and optional dependencies present). Skills
are declared and toggled in `configs/agents.yaml`.

```python
class Skill(Protocol):
    """A pluggable agent capability with an offline-checkable contract."""

    name: str

    def available(self) -> bool:
        """Return True when required dependencies and credentials exist."""

    def run(self, ctx: RunContext, **inputs: Any) -> SkillResult:
        """Execute the skill and record artifacts in the run manifest."""
```

Three shared pieces support all skills:

- **LLM client seam** (`llm.py`): one provider-agnostic `complete()` API with
  a recorded-stub mode that replays fixtures in tests. Every call is logged to
  the run manifest with model, tokens, and cost.
- **Artifact store** (`artifacts.py`): each paper run writes
  `runs/<run_id>/manifest.json` capturing skill results, input/output hashes,
  and seeds. The manifest is the reproducibility claim.
- **Prompt templates** in the existing empty `prompts/` package.

### Proposed package layout

```text
src/quantbench_crew/
  skills/
    __init__.py        # registry + config wiring
    base.py            # Skill protocol, SkillResult, RunContext
    scout/  reader/  coder/  bench/  reviewer/
  llm.py               # LLMClient protocol, provider adapters, recorded stub
  artifacts.py         # RunManifest and store helpers
  benchmarks/
    contract.py        # Strategy protocol, PanelData
    protocols.py       # walk-forward evaluation
    baselines.py       # equal weight, buy-and-hold, random-matched-turnover
  datasets/
    registry.py        # versioned, point-in-time dataset access
    french.py          # Kenneth French library loader
    synthetic.py       # planted-effect and pure-noise generators
  prompts/             # prompt template files
```

## New Dataclass Definitions

All new domain models follow the existing frozen-dataclass style in
`models.py`. Existing dataclasses gain only additive fields with defaults, so
current constructors and tests keep working.

### Evidence and claims

```python
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
```

### Method specification (reader output, coder input)

```python
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
```

### Generated implementation (coder output, bench input)

```python
@dataclass(frozen=True)
class StrategyArtifact:
    """Generated implementation produced by the coder."""

    paper: Paper
    code_path: Path                # module implementing the Strategy contract
    entry_point: str               # e.g. "build_strategy"
    test_paths: tuple[Path, ...] = ()
    plan: ImplementationPlan | None = None
    generation_manifest: dict[str, Any] = field(default_factory=dict)
```

The Strategy contract itself is a Protocol in `benchmarks/contract.py`, not a
dataclass. It is the keystone interface that finally lets the bench agent
consume the coder's output:

```python
class Strategy(Protocol):
    """Contract every generated implementation must satisfy.

    Implementations must be deterministic given (data, params, seed) and must
    not look ahead: weights as of time t may use only data up to t.
    """

    def fit(self, data: PanelData, train_end: date) -> None:
        """Estimate parameters using data up to train_end only."""

    def weights(self, data: PanelData, as_of: date) -> dict[str, float]:
        """Return target weights keyed by asset id, using data up to as_of."""
```

`PanelData` is a thin point-in-time wrapper over long-format
(date, asset, fields) records, defined alongside the contract (QB-09).

### Reviewer rubric

```python
@dataclass(frozen=True)
class RubricScore:
    """One scored dimension of the reviewer rubric."""

    dimension: str   # "reproducibility" | "robustness" | "net_of_cost_viability"
                     # | "novelty_vs_baselines" | "data_accessibility"
    score: int       # 0-4
    rationale: str
    evidence: tuple[EvidenceLink, ...] = ()
```

### Run plumbing (in `skills/base.py` and `artifacts.py`)

```python
@dataclass(frozen=True)
class SkillResult:
    """Outcome of one skill invocation, recorded in the run manifest."""

    skill: str
    status: str                    # "ok" | "skipped" | "failed"
    payload: dict[str, Any] = field(default_factory=dict)
    artifacts: tuple[str, ...] = ()   # paths relative to the run directory
    notes: tuple[str, ...] = ()


@dataclass
class RunContext:
    """Shared per-run state passed to every skill."""

    run_id: str
    run_dir: Path
    config: dict[str, Any]
    manifest: RunManifest
    llm: LLMClient | None = None


@dataclass
class RunManifest:
    """Reproducibility record for one paper run.

    Deliberately mutable: it accumulates results as the run progresses, then
    is serialized once to runs/<run_id>/manifest.json.
    """

    run_id: str
    paper_slug: str
    started_at: datetime
    config_hash: str
    skill_results: list[SkillResult] = field(default_factory=list)
    llm_calls: list[dict[str, Any]] = field(default_factory=list)
    seeds: dict[str, int] = field(default_factory=dict)
```

### Additive changes to existing models

- `PaperAnalysis` gains `method_spec: MethodSpec | None = None` and
  `reproduction_target: ReproductionTarget | None = None`.
- `BenchmarkResult` gains `comparisons: tuple[ClaimComparison, ...] = ()`.
- `ReviewReport` gains `rubric: tuple[RubricScore, ...] = ()`.

## Per-Agent Skill Roadmap

Priorities: P0 = Phase 1 critical path, P1 = Phase 2 deepening, P2 = later.

### QuantScoutAgent

- P0 Real arXiv search behind the existing `search_arxiv` seam (q-fin
  categories), plus Semantic Scholar enrichment (citations, venue, linked
  code repositories).
- P0 Reproducibility triage: classify data requirements as public, vendor, or
  proprietary (CRSP/TAQ imply WRDS access); detect released code; output a
  feasibility score that gates downstream spend.
- P1 Embedding-based relevance against a configurable research charter
  document; dedup against already-processed papers.

### QuantReaderAgent

- P0 PDF acquisition: arXiv URL to cached local file so PaperQA2 engages
  without hand-fed paths.
- P0 Target-table extraction: identify the headline results table and parse
  it into a `ReproductionTarget`. Without a quantitative target, reproduction
  is unfalsifiable.
- P0 MethodSpec extraction: structured, JSON-schema-validated extraction of
  universe, signal, construction, frequency, and sample period.
- P1 Falsifiable-claim enumeration and a red-flag scan (no transaction costs,
  in-sample tuning, survivorship-prone samples, microcap-driven results).

### QuantCoderAgent

- P0 Strategy contract plus one hand-written reference strategy (momentum)
  that passes through the bench harness. De-risks the contract before any
  code generation.
- P0 Code emission and sandboxed execution behind the existing ERA seams:
  `generate_fn` becomes LLM-backed code generation, `execute_fn` runs the
  candidate in a sandbox and scores on tests passed. This is the point where
  the UCB search starts doing real work.
- P1 Test synthesis from the MethodSpec: shape tests, determinism tests, and
  no-lookahead tests (shift inputs after t; outputs before t must not
  change). AST-level static checks (forbidden imports, no eval) before
  execution.

### QuantBenchAgent

- P0 Dataset registry: Kenneth French factor library and free daily prices
  first; synthetic generators with planted effects and pure noise for harness
  validation; vendor data (WRDS) as a pluggable tier later. Point-in-time
  discipline from day one.
- P0 Walk-forward protocol with purged/embargoed splits; baseline library
  (equal weight, buy-and-hold, momentum, random signals at matched turnover).
  Random nulls provide a significance floor.
- P1 Metrics suite: net-of-cost Sharpe with frequency-aware annualization
  (fixes the hard-coded sqrt(252)), turnover, capacity proxies, deflated
  Sharpe ratio, factor-spanning regression against FF5 plus momentum.
- P1 Claim comparison: achieved metrics versus `ReproductionTarget` within
  tolerance bands.

### QuantReviewerAgent

- P0 Rubric-based verdict where every line cites an `EvidenceLink`. Until
  real benchmarks flow, the verdict is hard-coded to "scaffold-only"; the
  current placeholder "promising" is worse than nothing.
- P1 Robustness interpretation (subsample stability, parameter sensitivity)
  and a quant-pitfalls red-team checklist auto-filled from upstream evidence.
- P2 Knowledge-grounded commentary: RAG over the practitioner corpus in
  `data/` (Dalio, Asness, Lopez de Prado, Chan, Fink source material) to
  contextualize findings against established practitioner views.

## Phase 1 Ticket Breakdown

Milestone: one golden paper end-to-end real. The golden paper enters via the
local JSON source with a cached PDF so the end-to-end test does not depend on
network arXiv; live arXiv fetch is exercised separately. Target method:
cross-sectional momentum, reproducible on free Kenneth French data.

Acceptance for the phase as a whole:

- Rerunning the pipeline on the golden paper yields identical manifest hashes
  (excluding timestamps).
- The pure-noise synthetic world produces an "inconclusive / does not
  reproduce" outcome.

Sizes: S (about a day), M (2-3 days), L (about a week).

### Workstream A: plumbing

- **QB-01 (M) Skill protocol, registry, config wiring.**
  Skills declared and toggled in `configs/agents.yaml`; agents resolve their
  skills through the registry. Done when existing behavior is unchanged with
  all skills disabled and unit tests cover registration, toggling, and
  fallback selection. Depends on: nothing.
- **QB-02 (M) LLM client seam.**
  One `complete()` API with provider adapters and a recorded-stub mode that
  replays fixtures in tests. Done when all LLM calls route through the seam
  and are logged to the manifest with model, tokens, and cost. Depends on:
  QB-01.
- **QB-03 (M) Run manifest and artifact store.**
  Every pipeline run writes `runs/<run_id>/manifest.json` with skill results,
  hashes, and seeds. Done when reruns with identical inputs produce identical
  hashes. Depends on: QB-01.
- **QB-04 (S) New domain models.**
  Add the dataclasses above; additive defaulted fields on existing models.
  Done when the full test suite passes unchanged. Depends on: nothing.

### Workstream B: scout and reader

- **QB-05 (M) Real arXiv search and PDF download.**
  `--source arxiv` returns live q-fin results; PDFs cached under `data/raw/`;
  deterministic offline fallback retained. Depends on: QB-01, QB-03.
- **QB-06 (M) Reproducibility triage skill.**
  Feasibility score and data-tier classification (public / vendor /
  proprietary) recorded per paper; gating threshold configurable. Depends on:
  QB-01, QB-04.
- **QB-07 (L) MethodSpec extraction skill.**
  PaperQA2/LLM-backed with metadata fallback. Done when the golden paper
  yields a MethodSpec with universe, frequency, signal, construction, and
  sample period; output is JSON-schema-validated; confidence recorded.
  Depends on: QB-02, QB-04.
- **QB-08 (M) Target-table extraction skill.**
  Done when the golden paper yields a `ReproductionTarget` with at least one
  Claim carrying value, tolerance, and source. Depends on: QB-02, QB-04.

### Workstream C: coder

- **QB-09 (M) Strategy contract, PanelData, reference momentum strategy.**
  Hand-written reference implementation with tests. Done when it passes the
  no-lookahead test and runs through the bench harness end to end. Depends
  on: QB-04.
- **QB-10 (M) Sandbox executor.**
  Extend `tools/code_runner.py`: no network, CPU/time/memory limits, fixed
  seeds, AST-based import allowlist. Done when fixture scripts that loop,
  fork, or import forbidden modules are blocked or killed with results
  captured. Depends on: nothing.
- **QB-11 (L) Code generation skill behind ERA.**
  LLM-backed `generate_fn` emits a Strategy module plus synthesized tests;
  `execute_fn` runs candidates in the sandbox; score is tests passed plus a
  structure score. Deterministic fallback generates from the reference
  strategy template. Done when, for the golden paper, at least one candidate
  passes all synthesized tests within the iteration budget. Depends on:
  QB-02, QB-07, QB-09, QB-10.

### Workstream D: bench

- **QB-12 (M) Dataset registry.**
  Kenneth French loader plus synthetic generators (planted momentum, pure
  noise) behind a point-in-time access API; datasets cached, hashed, and
  versioned in the manifest. Depends on: QB-03.
- **QB-13 (L) Walk-forward harness, baselines, frequency-aware metrics.**
  Purged/embargoed walk-forward; equal-weight, buy-and-hold, and
  random-matched-turnover baselines; metrics annualized by actual data
  frequency; configurable linear cost model in bps. Done when the reference
  momentum strategy beats random baselines on the planted-momentum world and
  does not on the noise world. Depends on: QB-09, QB-12.
- **QB-14 (S) Claim comparison.**
  Achieved metrics versus `ReproductionTarget` with tolerance bands, emitted
  as `ClaimComparison` records on `BenchmarkResult`. Depends on: QB-08,
  QB-13.

### Workstream E: reviewer and integration

- **QB-15 (M) Rubric verdict skill.**
  Evidence-linked rubric scores replace the static strengths/weaknesses;
  verdict is "scaffold-only" whenever placeholder data was used anywhere in
  the run. Done when two different papers produce different, evidence-cited
  reports. Depends on: QB-04, QB-14.
- **QB-16 (M) Golden-paper end-to-end test and synthetic-noise gate.**
  `pytest -m e2e` runs the full pipeline on the local golden record with
  cached PDF and recorded LLM fixtures; CI also runs the noise-world gate.
  Done when both pass deterministically in CI. Depends on: all of the above.

Suggested order: QB-01/QB-04 in parallel, then QB-02/QB-03/QB-10, then
workstreams B-D in parallel, closing with QB-11, QB-14, QB-15, QB-16.

## Later Phases (summary)

- **Phase 2:** the P1 items above, plus a golden-paper evaluation set (3-5
  papers with known-good reproductions, e.g. cross-sectional momentum, FF
  factors, Gu-Kelly-Xiu) run in CI as regression tests for the system itself.
- **Phase 3:** parallel paper runs, LLM call caching and per-paper cost caps,
  human-in-the-loop checkpoints before any "promising" verdict ships.

## Risks

- **Goodharting the reproduction target.** If `execute_fn` scores proximity
  to the paper's claimed Sharpe, the search will p-hack generated code toward
  matching the number rather than implementing the method faithfully.
  Mitigation: score primarily on spec-conformance tests; treat claim
  proximity as a sanity band, not the objective; keep an embargoed data
  segment the search never sees; cap iterations.
- **Leakage in generated code.** Mitigation: mandatory no-lookahead tests and
  point-in-time data contracts (QB-11, QB-12).
- **Silent LLM cost creep.** Mitigation: manifest-level spend tracking
  (QB-02) and per-paper budget caps (Phase 3).
- **Optional-dependency sprawl.** Mitigation: every skill implements
  `available()` and a deterministic fallback; the dry workflow remains the
  permanent baseline test target.
