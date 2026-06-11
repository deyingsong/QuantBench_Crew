# Phase 2 Design Note

Status: proposed
Date: 2026-06-10
Scope: deepen the Phase 1 walking-skeleton-made-real into a system that
ingests papers at scale, extracts and audits their claims from full text,
reproduces them on real (CRSP) and free (French) data, applies the
statistical rigor that separates signal from overfitting, and regression-tests
itself against a curated evaluation set in CI. No agent public API changes;
new behavior arrives as skills with deterministic offline fallbacks, exactly
as in Phase 1.

This note assumes Phase 1 (QB-01 .. QB-16) is complete: the skill registry,
LLM seam, run manifest, scout/reader/coder/bench/reviewer skills, the
Strategy/PanelData contract, the purged walk-forward harness with the
random-matched-turnover null, claim comparison, and the evidence-linked rubric
verdict all exist and are green, including the golden-paper e2e and the
synthetic-noise gate.

## Decisions baked into this plan

Two choices set the shape of Phase 2:

1. **Front-load extraction & ingestion depth.** The critical path is
   Workstream F (real arXiv at scale, charter-relevance ranking, PaperQA2
   full-text MethodSpec, falsifiable-claim enumeration, the quant-pitfalls
   red-flag scan). Statistical rigor and generation depth are planned but
   sequenced behind it. Rationale: Phase 1 proved the Coder->Bench seam on one
   hand-fed paper; the next bottleneck is getting *many* papers in with
   faithful, audited specs, because everything downstream is only as good as
   the MethodSpec and the ReproductionTarget it operates on.

2. **The evaluation set includes Gu-Kelly-Xiu on real CRSP data.** The
   operator is adding CRSP data under `data/`, so GKX becomes a genuine ML
   reproduction target rather than a synthetic proxy. This pulls a real
   point-in-time, survivorship-aware vendor data loader (QB-22) and an
   optional numerical stack (QB-23) onto the near-critical path, since the
   eval set cannot stand up without them.

## Guiding principles (carried + extended)

The four Phase 1 principles still hold (vertical slice first; skills are
plug-ins with deterministic offline fallbacks; evidence-linked outputs;
validate on synthetic truth before real papers). Phase 2 adds three:

5. **Real data earns real caveats.** The moment vendor data enters, so do
   survivorship bias, delisting returns, microcap illiquidity, and
   point-in-time fundamentals. A reproduction on CRSP that ignores these is
   not a reproduction. The data loader (QB-22) and the red-flag scan (QB-21)
   are the same conviction from two ends.
6. **Count every trial.** The manifest already records all candidates and
   seeds. Phase 2 makes that count load-bearing: the deflated Sharpe ratio and
   multiple-testing correction read the trial count out of the manifest, so a
   verdict that survived a wide search is haircut accordingly.
7. **The system regression-tests itself.** A reproduction harness that is not
   itself reproducible is worthless. The evaluation set (Workstream J) pins
   expected outcomes per paper — including papers that must *fail* to
   reproduce — and runs them in CI.

## New dataclass definitions

All additive and frozen, following `models.py`. Existing models gain only
defaulted fields, so Phase 1 constructors and tests keep working.

### Ingestion and audit (reader/scout)

```python
@dataclass(frozen=True)
class ResearchCharter:
    """Configurable statement of what research is in scope."""

    purpose: str
    themes: tuple[str, ...] = ()
    must_have: tuple[str, ...] = ()      # e.g. "out-of-sample test", "net of costs"
    exclude: tuple[str, ...] = ()        # e.g. "pure theory", "no empirics"
    source_path: str = ""


@dataclass(frozen=True)
class RelevanceAssessment:
    """Charter-relative relevance for one candidate paper."""

    score: float                         # 0-1
    method: str                          # "embedding" | "keyword_fallback"
    matched_themes: tuple[str, ...] = ()
    rationale: str = ""


@dataclass(frozen=True)
class RedFlag:
    """A detected quant-research pitfall, with the evidence for it."""

    kind: str        # "no_transaction_costs" | "in_sample_tuning"
                     # | "survivorship_prone" | "microcap_driven"
                     # | "short_sample" | "data_snooping"
    severity: str    # "info" | "warning" | "critical"
    rationale: str
    evidence: tuple[EvidenceLink, ...] = ()
```

### Statistical rigor (bench/reviewer)

```python
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
    p_value: float
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
```

### Evaluation harness (system regression)

```python
@dataclass(frozen=True)
class EvalCase:
    """One paper in the system's own regression suite."""

    slug: str
    paper: Paper
    data_tier: str                       # "french" | "crsp" | "synthetic"
    expected_outcome: str                # "reproduces" | "does_not_reproduce"
    targets: ReproductionTarget
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvalResult:
    """Outcome of running one EvalCase through the pipeline."""

    case: EvalCase
    achieved_verdict: str
    matches_expected: bool
    detail: str = ""
```

### Additive changes to existing models

- `PaperAnalysis` gains `relevance: RelevanceAssessment | None = None` and
  `red_flags: tuple[RedFlag, ...] = ()`.
- `BenchmarkResult` gains `spanning: SpanningResult | None = None`,
  `deflated_sharpe: DeflatedSharpe | None = None`, and
  `capacity: CapacityEstimate | None = None`.
- `ReviewReport` gains `robustness: RobustnessReport | None = None`.

## Workstream F: extraction & ingestion depth (critical path)

- **QB-17 (M) Live arXiv at scale + dedup.**
  Pagination, polite rate-limited backoff, and incremental date-window
  fetching behind the existing `search_arxiv` seam; a persistent
  processed-paper set (keyed by arxiv id and title hash) so re-runs skip work
  already done. Done when a multi-page q-fin query returns deduplicated
  results and a second run of the same window fetches nothing new. Depends on:
  QB-05.
- **QB-18 (M) Charter-relevance ranking.**
  A configurable `ResearchCharter` document; candidate abstracts scored
  against it via embeddings, feeding the scout ranking ahead of the keyword
  score. Optional embedding dependency with the Phase 1 keyword path as the
  deterministic fallback (`method="keyword_fallback"`). Done when relevance is
  recorded per paper and re-ranks a mixed candidate list sensibly. Depends on:
  QB-17.
- **QB-19 (L) PaperQA2 full-text MethodSpec extraction.**
  Drive PaperQA2 over the cached PDF (QB-05) to extract the MethodSpec from
  full text rather than the abstract, raising `extraction_confidence`; keep
  the metadata fallback. Hand-label MethodSpec fixtures for each eval paper as
  ground truth. Done when, for each eval paper, the extracted spec matches the
  hand-labeled fixture on universe/frequency/signal/construction/sample within
  a stated field-match rate. Depends on: QB-02, QB-07.
- **QB-20 (M) Falsifiable-claim enumeration.**
  Extend target-table extraction from the single headline claim to the full
  set of falsifiable quantitative claims, each a `Claim` in the
  `ReproductionTarget`. Done when a multi-result paper yields multiple claims
  with values, tolerances, and sources, schema-validated. Depends on: QB-08.
- **QB-21 (M) Quant-pitfalls red-flag scan.**
  Detect no-transaction-costs, in-sample tuning, survivorship-prone samples,
  microcap-driven results, short samples, and data-snooping language; emit
  `RedFlag` records with evidence. Checklist seeded from the Lopez de Prado
  material in `Source_data/transcript/`. Done when planted red-flag abstracts
  are caught and a clean abstract is not. Depends on: QB-19 (full text
  sharpens detection; abstract-only works as a first pass).

## Workstream G: real data tiers (enables GKX + survivorship-aware repro)

### Operator data inventory (confirmed present under `data/raw/`)

Modern CRSP CIZ daily flat files, US stocks, 2015-01-02 .. 2024-12-31,
~1.18M daily security-rows, CSV with CamelCase headers and ISO dates:

- `stock/daily_stock_file_15-24.csv` (683 MB) — one row per (PERMNO, day).
  Load-bearing columns: `PERMNO` (security id), `DlyCalDt` (date), `DlyRet`
  (daily total return, dividends in), `DlyRetx` (price-only), `DlyCap` (market
  cap, for size and value-weighting), `DlyPrc`/`DlyClose` (price filters),
  `DlyVol`/`DlyPrcVol` (volume / dollar volume, for illiquidity and capacity),
  `PrimaryExch`, `SICCD`, `ShareType`/`SecurityType`/`IssuerType` (common-stock
  filters), `ShrOut`. Index returns (`vwretd`, `ewretd`, `sprtrn`) are appended
  per row and also stand alone in `daily_stock_market_indexes_15-24.csv`.
- `stock/delisting_information_15-24.csv` — `PERMNO`, `DelistingDt`, `DelRet`:
  the delisting returns to splice so the universe is survivorship-bias-free.
- `stock/names_15-24.csv`, `stock/stock_header_information_15-24.csv` —
  point-in-time identity/exchange/SIC history.
- `Stock_Version2_CIZ/*_variable_reference.csv` — the field dictionaries above.

This is daily data with **no Compustat fundamentals**, so the characteristic
set for ML is the price/volume/return-derived subset (momentum at several
horizons, short-term reversal, size, Amihud illiquidity, realized volatility,
volume trend, max daily return, turnover) — not GKX's full 94. The eval case
is scoped accordingly (QB-34).

> **Resolved — PDF is out of scope; ML case is GKX-style.**
> `data/raw/2606.08586v1.pdf` is *not* Gu-Kelly-Xiu. It is Ozimek,
> "Cross-sectional topological anomaly scores and intraday return
> predictability in the S&P 500" (BallMapper + decoder-conditional VAE +
> function-on-function regression), which needs **intraday** data for ten S&P
> 500 names over Apr 2025–Mar 2026 — not present here and not reconstructable
> from the daily CIZ file. Operator decision (2026-06-10): keep the GKX-*style*
> ML reproduction on constructed daily-CIZ characteristics (QB-34); the Ozimek
> paper is out of scope unless its intraday dataset is supplied later, at which
> point it would be a separate eval case with intraday TDA features rather than
> a cross-sectional daily one.

- **QB-22 (L) CRSP CIZ dataset loader.**
  Stream the daily file into point-in-time monthly `PanelData` keyed by
  `PERMNO`: aggregate daily `DlyRet` to monthly compounded returns; build a
  survivorship-bias-free universe per month from `SecurityBegDt`/`EndDt` and
  `DelistingDt`, splicing `DelRet` in the delisting month; apply configurable
  common-stock (`ShareType`/`SecurityType`), exchange (`PrimaryExch`), and
  microcap (`DlyPrc`/`DlyCap` percentile) filters; derive the price/volume
  characteristic fields listed above. Registered as the `crsp` vendor tier;
  content-hashed and versioned in the manifest. Memory-safe streaming (the
  daily file is 683 MB), with a small cached monthly panel as the working
  artifact. Done when the loader reconstructs a point-in-time universe with no
  look-ahead (a date-`t` panel contains no security absent at `t` and no
  post-`t` data) and the reference momentum strategy runs on it end to end.
  Depends on: QB-12, QB-23.
- **QB-23 (S) Optional numerical stack tier.**
  A `numeric` optional-dependency group (numpy, pandas, scikit-learn) for the
  real-data and ML paths; every skill that uses it implements `available()`
  and the dry, stdlib-only workflow remains the permanent baseline. Done when
  the suite passes with the group absent and the numeric paths activate when
  present. Depends on: nothing.

## Workstream H: statistical rigor (metrics suite + reviewer robustness)

- **QB-24 (M) Metrics suite deepening.**
  Capacity proxies (`CapacityEstimate`), and the deflated Sharpe ratio
  (`DeflatedSharpe`) computed with the trial count read from the manifest.
  Pure-Python where feasible to preserve determinism. Done when a wide search
  visibly haircuts the deflated Sharpe relative to the observed one. Depends
  on: QB-13, QB-14.
- **QB-25 (M) Factor-spanning regression.**
  Regress candidate returns on FF5 + momentum (free French factors); report
  alpha, t-stat, betas, R-squared, residual Sharpe as a `SpanningResult` on
  `BenchmarkResult`. Pure-Python OLS. Done when a pure-momentum strategy shows
  a large MOM beta and near-zero spanning alpha against a set including MOM.
  Depends on: QB-13.
- **QB-26 (M) Multiple-testing correction.**
  Aggregate the manifest's trial count (candidates x seeds x parameterizations)
  into the deflation and a family-wise / FDR adjustment surfaced to the
  reviewer. Done when the noise-world false-positive rate, already low,
  provably tightens further under correction. Depends on: QB-24.
- **QB-27 (L) Robustness interpretation.**
  Subsample stability (split-sample and rolling) and parameter-sensitivity
  sweeps, emitted as a `RobustnessReport`. Done when a fragile (overfit)
  parameterization is flagged sign-unstable and the reference momentum is not.
  Depends on: QB-13, QB-22.
- **QB-28 (M) Quant-pitfalls red-team checklist in the reviewer.**
  Auto-fill a robustness rubric dimension and a red-team checklist from
  upstream `RedFlag`s and the `RobustnessReport`; rubric language seeded from
  risk-review rubrics plus the practitioner corpus. Done when two papers with
  different pitfalls produce different, evidence-cited red-team sections.
  Depends on: QB-15, QB-21, QB-27.

## Workstream I: generation depth (planned, deferred)

Sequenced last per the front-loading decision; may proceed in parallel with H
and J once F and G land.

- **QB-29 (M) Spec-specific test synthesis.**
  LLM-derived tests beyond the deterministic templates: edge cases implied by
  the signal formula, sample-period boundaries, construction-specific
  invariants. Depends on: QB-11, QB-19.
- **QB-30 (L) Vetted numerical sandbox allowlist.**
  Extend the sandbox import allowlist to a pinned, vetted numerical subset
  (numpy, pandas, scikit-learn) so *generated* ML strategies can run; re-run
  the threat model, keep resource caps, and keep the stdlib-only tier as the
  default. Done when a generated numpy strategy executes and a forbidden
  import still blocks. Depends on: QB-10. (Reviewed via `/ecc:security-review`.)
- **QB-31 (L) Agentic codegen adapter.**
  Implement the reserved `agent` adapter behind the QB-11 two-adapter seam:
  headless Claude Code / Agent SDK generate-test-fix loop, cost-capped via the
  existing per-paper cap. Done when the agent adapter produces a
  template-passing candidate within budget on the golden paper. Depends on:
  QB-11, QB-02.
- **QB-32 (L) Generated strategies through the bench.**
  Run sandboxed generated candidates in the walk-forward harness (not just the
  template tests), closing the Coder->Bench seam for generated code. Done when
  a generated momentum candidate produces a `BenchmarkResult` matching the
  trusted reference within tolerance. Depends on: QB-30, QB-31, QB-13.

## Workstream J: golden evaluation set + CI

- **QB-33 (M) Evaluation harness.**
  `EvalCase` / `EvalResult` models; run each case through the pipeline, compare
  the achieved verdict to the expected outcome, emit a regression report. Done
  when the harness correctly passes a case expected to reproduce and a case
  expected not to. Depends on: QB-13, QB-14, QB-15.
- **QB-34 (L) The evaluation set.**
  The curated papers with hand-labeled targets and expected outcomes:
  - cross-sectional momentum (French) — *reproduces* (already green);
  - size and value / HML (French) — *reproduces*;
  - profitability / RMW (French) — *reproduces*;
  - Gu-Kelly-Xiu-style ML cross-section (CRSP) — *reproduces*. Scoped to the
    price/volume characteristic subset constructible from the daily CIZ file
    (no Compustat fundamentals; see the data inventory). The reproduction
    target is GKX's *qualitative* finding — a nonlinear ML model extracts
    cross-sectional return predictability that beats both a linear model and
    the random-matched-turnover null out-of-sample — not GKX's exact R² on a
    different sample period (2015-2024 vs their 1957-2016);
  - a **negative control** (confirmed in scope) — a deliberately
    data-snooped / placebo signal that must *not* reproduce. The cheapest,
    highest-signal regression guard: the noise-gate generalized to a named
    "should-fail" case.
  Depends on: QB-19, QB-20, QB-22, QB-24, QB-25, QB-33.
- **QB-35 (M) CI integration.**
  `pytest -m eval` runs the set with recorded LLM fixtures and cached data;
  gates on any case whose outcome diverges from expectation; cost-capped.
  Done when the suite passes deterministically in CI and a deliberately
  broken extractor turns a green case red. Depends on: QB-34.

## Suggested order

F and G first and in parallel (extraction depth alongside the real-data tier
the eval set needs): QB-17/QB-23 to start, then QB-18/QB-19/QB-22, then
QB-20/QB-21. H next (QB-24/QB-25 in parallel, then QB-26, then QB-27/QB-28).
J closes the phase (QB-33, then QB-34, then QB-35). I (QB-29..QB-32) runs in
parallel with H/J once F and G are stable. The three L-sized, externally
dependent tickets — QB-19 (PaperQA2), QB-22 (CRSP), QB-31 (agentic codegen) —
each get an `/ecc:plan` pass before implementation and `/ecc:python-review` on
completion.

## Phase 2 acceptance

- Each evaluation case's achieved verdict matches its expected outcome
  deterministically in CI, including the negative control failing to
  reproduce.
- GKX reproduces on real CRSP data through the ML path, with its spanning
  alpha and deflated Sharpe reported and survivorship handled.
- Every "reproduces" verdict in the set carries a deflated Sharpe (haircut by
  the manifest trial count), a factor-spanning result, and a robustness
  report — no verdict rests on a raw in-sample Sharpe.

## Risks

- **CRSP point-in-time correctness.** Survivorship and look-ahead are easy to
  reintroduce in a vendor loader. Mitigation: QB-22's done-criteria require a
  no-look-ahead universe reconstruction test, and QB-21's red-flag scan plus
  QB-27's robustness checks are an independent second line.
- **Extraction confidence inflation.** Full-text extraction can look
  authoritative while being wrong. Mitigation: hand-labeled fixtures per eval
  paper (QB-19) are the ground truth; `extraction_confidence` is reported, not
  trusted.
- **Numerical-stack determinism.** numpy/sklearn introduce platform and
  threading nondeterminism. Two-tier policy (operator-confirmed): the stdlib
  dry workflow stays bit-exact (identical manifest content hash on rerun), and
  the numeric/real-data paths use **tolerance-banded** reproducibility —
  pinned versions, fixed seeds, capped thread counts, and tolerance-banded
  (not bit-exact) assertions. Manifests on the numeric path therefore record
  metric values within a tolerance rather than a bit-exact hash; the eval
  harness (QB-33) compares verdicts and banded metrics, not hashes.
- **Eval-set overfitting the harness.** Tuning the system until the eval set
  passes is the meta-version of the very sin the project exists to catch.
  Mitigation: the negative control and the synthetic-noise gate stay in the
  set as permanent should-fail anchors; expand the set faster than it is
  tuned.
- **Generation depth vs the sandbox.** Allowing numpy/sklearn into the sandbox
  (QB-30) widens the attack surface for generated code. Mitigation: a pinned,
  vetted subset only; re-threat-modeled; isolated-subprocess + rlimits posture
  unchanged; security-reviewed before merge.
```
