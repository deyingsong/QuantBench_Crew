# QuantBench Crew

A multi-agent research assistant that discovers quantitative finance papers,
extracts their methods and claims, generates and sandbox-tests candidate
implementations, benchmarks them on synthetic and real market data, and issues
an evidence-linked verdict on whether the paper's headline result actually
reproduces.

Its defining trait is statistical honesty: every trial is counted in a run
manifest, observed Sharpe ratios are deflated for selection bias, candidates
must beat a random-matched-turnover null, and the reviewer refuses to call
anything "promising" that rests on placeholder data or an uncorrected search.
It does not make trading decisions, execute trades, or provide financial
advice.

## Quick start

```bash
# 1. Create and activate the environment (Python 3.11+)
conda env create -f environment.yml
conda activate quantbench-crew

# 2. Run the deterministic dry workflow — no network, no API keys
quantbench run --source local --max-papers 2

# 3. Run the test suite
pytest              # fast suite (~25s)
pytest -m e2e       # golden-paper end-to-end + synthetic-noise gate
pytest -m eval      # system regression suite over the curated eval set (slow)
```

The dry run prints a Markdown review report per paper and writes a
reproducibility manifest to `runs/<run_id>/manifest.json`. Everything beyond
the dry workflow — live arXiv search, LLM-backed extraction, code generation,
real-data benchmarking — is an opt-in *skill* toggled in
[configs/agents.yaml](configs/agents.yaml); the sections below explain each
tier. Always run commands inside the conda environment.

---

## Detailed documentation

### 1. How it works

Five agents form a pipeline; each paper flows through all of them and every
step records its results in the run manifest:

```
 arXiv / local JSON
        |
   QuantScout      rank by keywords + research-charter relevance;
        |          reproducibility triage gates infeasible papers early
   QuantReader     PDF acquisition -> full-text MethodSpec extraction ->
        |          falsifiable-claim enumeration -> quant-pitfalls red flags
   QuantCoder      ERA (Flat UCB) search over candidate strategy modules,
        |          each scored in a sandbox against deterministic test
        |          templates (shape / determinism / no-lookahead / invariants)
   QuantBench      purged+embargoed walk-forward on a registered dataset,
        |          baselines incl. a random-matched-turnover null, net-of-cost
        |          frequency-aware metrics, deflated Sharpe, factor spanning,
        |          robustness sweeps, claim comparison vs the paper's numbers
   QuantReviewer   evidence-linked rubric scores + red-team checklist ->
        |          verdict: scaffold-only | weak | inconclusive | promising
        v
 report.md + runs/<run_id>/manifest.json
```

Two design rules hold everywhere:

- **Skills are plug-ins; agents are orchestrators.** Each capability is a
  named skill with an availability check and a deterministic offline fallback.
  All skills ship disabled, so the default pipeline is a dependency-free,
  bit-exact dry run, and enabling any subset never breaks the rest.
- **Count every trial.** The manifest records every candidate, baseline, seed,
  LLM call (with cost), and artifact hash. The deflated Sharpe ratio reads its
  trial count from the manifest, so a result found by a wide search is
  haircut accordingly — selection bias is treated as the primary enemy.

### 2. Install

Recommended (conda, includes PaperQA2):

```bash
conda env create -f environment.yml
conda activate quantbench-crew
```

Minimal (any Python 3.11+ environment):

```bash
pip install -e ".[dev]"          # core + pytest; stdlib + PyYAML only
```

Optional tiers — the dry workflow never requires any of these:

| Extra / package        | Enables                                                        |
| ---------------------- | -------------------------------------------------------------- |
| `pip install -e ".[paperqa]"` | PaperQA2 full-text document reading in the reader        |
| `pip install anthropic`       | the live LLM provider (`llm.provider: anthropic`)        |
| `pip install -e ".[numeric]"` | numpy/pandas/scikit-learn for generated ML strategies in the sandbox (`quantbench_crew.numeric` reports availability) |

### 3. Running the pipeline

```bash
quantbench run [options]         # or: python -m quantbench_crew.main
```

| Flag | Default | Meaning |
| --- | --- | --- |
| `--source {local,arxiv}` | `local` | built-in/JSON records, or live arXiv q-fin search |
| `--query` | `"quantitative finance"` | search query (arxiv source) |
| `--max-papers` | `2` | papers to process |
| `--paper-json PATH` | – | local JSON list of paper records |
| `--agents-config PATH` | `configs/agents.yaml` | agent + skill configuration |
| `--benchmark-config PATH` | `configs/benchmarks.yaml` | benchmark defaults |
| `--report-dir PATH` | `reports` | report output dir (with `--write-reports`) |
| `--write-reports` | off | also write `reports/<slug>.md` |
| `--runs-dir PATH` | `runs` | manifest dir; each paper writes `<runs-dir>/<run_id>/manifest.json` |
| `--processed-path PATH` | `data/processed/seen_papers.json` | cross-run dedup watermark (arxiv source) |
| `--no-dedup` | off | disable the processed-paper watermark |

**Full pipeline without API keys.** Copy `configs/agents.yaml`, flip
`enabled: true` on the skills you want, and run against the golden paper —
with `llm.provider: none` every LLM-backed skill downgrades to its
deterministic fallback, so this exercises extraction, code generation,
sandboxing, walk-forward benchmarking, and the rubric verdict end to end:

```bash
quantbench run --paper-json tests/fixtures/golden_paper.json \
  --agents-config my-agents.yaml --max-papers 1
```

**Live arXiv** (network; results deduplicated against previous runs):

```bash
quantbench run --source arxiv --query "cross-sectional momentum" --max-papers 5
```

### 4. Configuration (`configs/agents.yaml`)

The top-level `llm:` section configures the one seam every LLM call routes
through:

```yaml
llm:
  provider: none          # none | stub | anthropic
  model: claude-opus-4-8
  fixtures: tests/fixtures/llm_fixtures.json   # stub provider replays these
  cost_cap_usd: 2.0       # per-paper spend cap, enforced mid-search
```

- `none` — no client; every skill uses its deterministic fallback.
- `stub` — replays recorded fixtures keyed by request fingerprint (tests/CI).
- `anthropic` — live API; needs `pip install anthropic` and `ANTHROPIC_API_KEY`
  (or `ANTHROPIC_AUTH_TOKEN`) in the environment. Every call is logged to the
  manifest with model, tokens, and cost; the cost cap stops generation loops.

`quant_scout.charter` defines what research is in scope (purpose, themes,
must-haves, exclusions); when the `charter_relevance` skill is enabled it
dominates the keyword ranking. `.env.example` holds PaperQA2-related settings
(`OPENAI_API_KEY` is PaperQA2's default backend, distinct from the pipeline's
own LLM seam).

Per-agent skills, all shipped `enabled: false`:

| Agent | Skill | When enabled |
| --- | --- | --- |
| scout | `charter_relevance` | score candidates against the research charter; boost ranking |
| scout | `reproducibility_triage` | data-tier classification (public/vendor/proprietary) + feasibility score; gates papers below `threshold` |
| reader | `pdf_acquisition` | resolve arXiv URL → cached PDF under `cache_dir` so PaperQA2 engages |
| reader | `method_spec_extraction` | schema-validated MethodSpec (LLM/full-text → metadata fallback), confidence recorded |
| reader | `target_table_extraction` | enumerate falsifiable claims into a ReproductionTarget with tolerance bands |
| reader | `red_flag_scan` | detect quant pitfalls (no costs, in-sample tuning, survivorship, microcaps, short sample, snooping) |
| coder | `code_generation` | ERA search over candidate modules; `adapter: complete` (single-shot LLM) or `agent` (headless Claude Code, used when available, otherwise falls back) |
| bench | `dataset_registry` | load + provenance-hash the configured `dataset` into the manifest |
| bench | `walk_forward` | purged/embargoed walk-forward vs baselines; deflated Sharpe; spanning (set `factors_path`); claim comparison |
| reviewer | `rubric_verdict` | evidence-linked rubric + red-team checklist → honest verdict |

Enabled skills record results in manifests, so a runs directory is required
(the default `runs/` satisfies this).

### 5. Data

Everything under `data/raw/` and `data/processed/` is gitignored. The dataset
registry (`quantbench_crew.datasets.registry`) resolves these names, each
content-hashed and versioned into the manifest:

| Dataset name | Source | Notes |
| --- | --- | --- |
| `planted_momentum` | synthetic | persistent cross-sectional drift; momentum *must* work here |
| `pure_noise` | synthetic | zero-mean iid returns; nothing may "reproduce" here |
| `french_momentum` | `data/raw/french_momentum_monthly.csv` | Kenneth French momentum portfolios; long CSV `YYYYMM,portfolio,return_pct` |
| `crsp` | `data/raw/stock/` | CRSP CIZ daily flat files → point-in-time monthly panel |

The CRSP loader streams the daily file with the stdlib `csv` module (no
pandas; ~8s for 683 MB), compounds daily to monthly returns, builds a
survivorship-bias-free universe by construction, splices delisting returns
(`DelRet`) into each name's final month, applies configurable common-stock /
exchange / price / cap-percentile filters, and derives price/volume
characteristics (cap, dollar volume, return vol, max daily return). Expected
files:

```
data/raw/stock/daily_stock_file_15-24.csv        # PERMNO,DlyCalDt,DlyRet,DlyCap,DlyPrc,DlyPrcVol,PrimaryExch,SecurityType,ShareType,...
data/raw/stock/delisting_information_15-24.csv   # PERMNO,DelistingDt,DelRet,...
data/raw/ff_factors_monthly.csv                  # optional: YYYYMM + FF5/MOM columns (percent) for spanning
```

### 6. Benchmarking and statistics

The walk-forward protocol refits per train window and evaluates strictly
out-of-sample, with a purge gap (sized to the strategy's formation window) and
an embargo between folds. Each candidate is compared against equal-weight,
buy-and-hold, and a **random-matched-turnover null** — random selection with
the candidate's sizing, so it pays the same costs while carrying no signal.

Metrics are frequency-aware (monthly data annualizes with √12, not √252) and
net of a linear cost model (`cost_bps` per unit turnover). On top of the raw
metrics:

- **Deflated Sharpe ratio** (Bailey–López de Prado): haircuts the observed
  Sharpe by the manifest's trial count and trial dispersion; reported with a
  p-value.
- **Factor spanning**: pure-Python OLS of candidate returns on FF5+momentum;
  alpha, t-stat, betas, R², residual Sharpe.
- **Robustness**: split-sample/rolling subsample Sharpes (sign stability) and
  parameter-sensitivity sweeps.
- **Claim comparison**: achieved metrics vs the paper's extracted claims
  within per-claim tolerance bands — reported as a sanity band, never used as
  an optimization objective.

The reviewer only says **promising** when the candidate beats the random
null, survives deflation, is sign-stable across subsamples, and carries no
critical red flag; placeholder data anywhere forces **scaffold-only**.

### 7. Code generation and the sandbox

The coder runs an ERA Flat-UCB search whose `generate_fn` emits candidate
strategy modules and whose `execute_fn` scores them in a sandbox against
deterministic test templates: shape, determinism, no-lookahead (weights at *t*
must not change when post-*t* data is perturbed), plus construction-aware
invariants derived from the MethodSpec (e.g. long-short ⇒ zero net weight).
The deterministic fallback candidate is the hand-written reference momentum
strategy, so the search's worst case is a known-good implementation.

Untrusted candidate code never executes in the host interpreter. The sandbox
([code_runner.py](src/quantbench_crew/tools/code_runner.py)) layers an AST
gate (import allowlist; `eval`/`exec`/`open`/`getattr`/dunder access banned)
over an isolated subprocess (`-s -P -B`, scrubbed environment, CPU/memory/
file-size/process rlimits, pinned hash seed). A vetted numeric allowlist
(numpy/pandas/sklearn/scipy) can be opted into for generated ML strategies;
the stdlib-only allowlist stays the default. Generated strategies can also be
backtested *inside* the sandbox (`benchmarks/sandbox_backtest.py`), so even
benchmarking never trusts generated code host-side.

Two generation adapters share the seam: `complete` (single-shot emission
through the LLM client) and `agent` (headless Claude Code generate-test-fix
loop, used only when the CLI and credentials are present, otherwise it falls
back loudly). Both are bounded by the per-paper cost cap.

### 8. Reproducibility and manifests

Every paper run writes `runs/<run_id>/manifest.json`: config hash, every
skill result, every LLM call (model/tokens/cost), seeds, dataset provenance
(name/version/content hash), and artifact hashes (generated code, benchmark
JSON, the report itself).

Determinism is two-tier:

- the stdlib dry workflow is **bit-exact** — rerunning on identical inputs
  yields an identical manifest `content_hash` (volatile fields excluded);
- real-data/numeric paths are **tolerance-banded** — pinned seeds and banded
  assertions rather than hash equality.

### 9. Evaluation set and tests

The system regression-tests *itself* against curated cases with hand-labeled
expected outcomes (`pytest -m eval`, deselected by default):

| Case | Data | Expected | Why |
| --- | --- | --- | --- |
| `momentum_planted` | synthetic planted drift | reproduces | the harness must find a real signal |
| `noise_control` | pure noise | does **not** reproduce | negative control: over-claiming fails CI |
| `momentum_crsp` | CRSP 2015–2024 | does **not** reproduce | JT momentum didn't persist at claimed magnitude in this decade — honest ground truth |
| `gkx_ml_crsp` | CRSP 2015–2024 | does **not** reproduce | GKX-style linear ML beats the null (Sharpe ≈ 0.4) but fails deflation on the price/volume feature subset |

That last row is the project's thesis in miniature: the system beats the null
yet *declines* to claim a reproduction, because the deflated-Sharpe bar is not
cleared. Suite totals: **210 tests** (fast suite + `e2e` + `eval` markers);
CRSP-backed cases skip automatically when the data is absent.

### 10. Repository layout

```text
configs/                  agents.yaml (skills + llm + charter), benchmarks.yaml
data/raw|processed/       market data + caches (gitignored)
docs/                     architecture.md, skills-design.md, phase2-design.md, phase2-status.md
runs/                     per-run manifests + artifacts (gitignored)
reports/                  written reports (--write-reports)
src/quantbench_crew/
  agents/                 the five agents + the ERA search
  skills/                 registry + per-agent skill implementations
  benchmarks/             Strategy contract, PanelData, walk-forward, baselines,
                          metrics, statistics (DSR), spanning, robustness, claims,
                          strategies registry, sandboxed backtest
  datasets/               registry, synthetic worlds, French + CRSP loaders, eval set
  tools/                  arXiv client + dedup, sandbox runner, parsers
  llm.py                  provider-agnostic LLM seam (none/stub/anthropic, cost log)
  artifacts.py            run manifest + artifact store (content hashing)
  prompts/                prompt templates
tests/                    210 tests incl. e2e and eval markers
```

### 11. Project status and docs

Phases 1 and 2 of the design are complete (tickets QB-01…QB-35). Read, in
order: [docs/skills-design.md](docs/skills-design.md) (Phase 1 design),
[docs/phase2-design.md](docs/phase2-design.md) (Phase 2 design + as-built
empirical findings), [docs/phase2-status.md](docs/phase2-status.md) (current
status). Known gaps: value/profitability sorts and the full nonlinear GKX
reproduction need Compustat fundamentals; Phase 3 (parallel runs, LLM
caching, human-in-the-loop checkpoints) is unstarted.

## Disclaimer

QuantBench Crew is a research-support tool. Outputs must be reviewed by
qualified human researchers before being used in any investment, trading,
risk management, or production decision-making process.
