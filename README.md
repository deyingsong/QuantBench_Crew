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

Each run writes, per paper, a review report (`reports/<slug>.md`), the
generated strategy implementation (`reports/<slug>_strategy.py`), and a
reproducibility manifest (`runs/<run_id>/manifest.json`); the report is also
printed to stdout (`--no-write-reports` disables the files). Code generation
runs by default with a deterministic offline fallback; everything else beyond
the dry workflow — live arXiv search, LLM-backed extraction, real-data
benchmarking — is an opt-in *skill* toggled in
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
| `--source NAME` | `local` | `local` (JSON records), `arxiv` (live q-fin search), a conference — `kdd`, `icml`, `iclr`, `wsdm`, `aaai`, `ijcai`, `www` (ACM Web Conference), `neurips` — a journal — `jf`, `jfe`, `rfs` — or a group: `conferences`, `journals` |
| `--query` | `"quantitative finance"` | search query (non-local sources) |
| `--query-pool SEL` | – | search a curated query pool instead of one query: `auto` (each venue's matched pool), a pool name (`roots`, `finance`, `general-ai`, `core-ml`, `data-mining`), `pool/category`, or `all`; mutually exclusive with `--query` |
| `--year N` | – | restrict conference/journal sources to one publication year |
| `--max-papers` | `2` | papers to process (split across a group's venues) |
| `--paper-json PATH` | – | local JSON list of paper records |
| `--agents-config PATH` | `configs/agents.yaml` | agent + skill configuration |
| `--benchmark-config PATH` | `configs/benchmarks.yaml` | benchmark defaults |
| `--report-dir PATH` | `reports` | report output dir |
| `--write-reports / --no-write-reports` | **on** | write `reports/<slug>.md` + the generated `reports/<slug>_strategy.py` per paper |
| `--runs-dir PATH` | `runs` | manifest dir; each paper writes `<runs-dir>/<run_id>/manifest.json` |
| `--processed-path PATH` | `data/processed/seen_papers.json` | cross-run dedup watermark (arxiv source) |
| `--no-dedup` | off | disable the processed-paper watermark |

**Full pipeline, with or without API keys.** Copy `configs/agents.yaml`, flip
`enabled: true` on the skills you want, and run against the golden paper. The
shipped `llm.provider: per-agent` uses each agent's live backbone when its
API key is present and downgrades that agent to its deterministic fallback
when it is not — so the same command exercises extraction, code generation,
sandboxing, walk-forward benchmarking, and the rubric verdict end to end
either way (set `llm.provider: none` to force everything offline):

```bash
quantbench run --paper-json tests/fixtures/golden_paper.json \
  --agents-config my-agents.yaml --max-papers 1
```

**Live sources** (network; results deduplicated against previous runs by
arXiv id / DOI / title watermark):

```bash
quantbench run --source arxiv --query "cross-sectional momentum" --max-papers 5
quantbench run --source neurips --query "portfolio optimization" --year 2024 --max-papers 5
quantbench run --source jfe --query "momentum" --max-papers 3
quantbench run --source conferences --query "return prediction" --max-papers 8
```

Conferences (KDD, ICML, ICLR, WSDM, AAAI, IJCAI, WWW, NeurIPS) are searched
via DBLP's canonical venue streams, with abstracts and open-access PDF links
enriched from OpenAlex in one batched DOI lookup; journals (Journal of
Finance, Journal of Financial Economics, Review of Financial Studies) are
searched via OpenAlex filtered by ISSN. Both backends are keyless; on network
failure each source falls back to deterministic offline placeholders.

Two search-semantics notes: conference queries match paper **titles** (DBLP
indexes titles, not abstracts), so prefer short title-like terms ("portfolio",
"stock prediction") over phrases; journal queries match full metadata
including abstracts. Papers without a DOI (common for NeurIPS proceedings)
cannot be abstract-enriched and arrive title-only; the finance journals are
paywalled, so expect metadata + abstract rather than full-text PDFs unless a
paper has an open-access copy.

**Curated query pools.** Instead of a single `--query`, `--query-pool` fans
the paper budget across a curated term list with cross-term dedup (each hit
records the term that found it in `raw["query"]`). Pools are matched to
source semantics — `finance` (empirical asset pricing, market microstructure,
momentum strategy, …) for JF/JFE/RFS; `general-ai` (LLM trading bots,
multi-agent simulation, algorithmic trading, …) for AAAI/IJCAI; `core-ml`
(time-series foundation models, Mamba, diffusion models, deep RL, …) for
ICML/ICLR/NeurIPS; `data-mining` (GNNs, sentiment analysis, spatiotemporal
forecasting, …) for KDD/WSDM/WWW; plus seven high-yield `roots` (portfolio,
asset pricing, time series, trading, stock, volatility, alpha). `auto`
resolves each venue to its matched pool, so one command scouts every venue
with the right vocabulary:

```bash
quantbench queries                                           # browse the pools
quantbench run --source conferences --query-pool auto --max-papers 16
quantbench run --source jfe --query-pool finance/market-mechanics --max-papers 5
quantbench run --source neurips --query-pool core-ml/generative-synthetic --year 2024
```

### 4. Configuration (`configs/agents.yaml`)

The top-level `llm:` section configures the one seam every LLM call routes
through. The shipped default is **per-agent backbones**: each agent gets its
own provider, matched to the agent's job:

```yaml
llm:
  provider: per-agent     # none | stub | per-agent | <single provider name>
  model: claude-opus-4-8  # default for single-provider modes
  fixtures: tests/fixtures/llm_fixtures.json   # stub provider replays these
  cost_cap_usd: 2.0       # per-paper spend cap across ALL backbones
  agents:
    quant_scout:    {provider: grok,      model: grok-4}
    quant_reader:   {provider: gemini,    model: gemini-2.5-pro}
    quant_coder:    {provider: anthropic, model: claude-opus-4-8}
    quant_bench:    {provider: deepseek,  model: deepseek-chat}
    quant_reviewer: {provider: openai,    model: gpt-5}
```

| Agent | Backbone | Port (API-key env var) | Why this match |
| --- | --- | --- | --- |
| scout | Grok (xAI) | `XAI_API_KEY` (or `GROK_API_KEY`) | discovery/triage of fresh papers; real-time orientation, cheap bulk scoring |
| reader | Gemini | `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) | long-document method/claim extraction; long context |
| coder | Claude | `ANTHROPIC_API_KEY` (or `ANTHROPIC_AUTH_TOKEN`) | strongest code generation; synergy with the headless-Claude agent adapter |
| bench | DeepSeek | `DEEPSEEK_API_KEY` | numeric/statistical interpretation; strong math reasoning at low cost |
| reviewer | GPT (OpenAI) | `OPENAI_API_KEY` | final synthesis and red-team critique; balanced general reasoning |

Copy `.env.example` for the full list of ports. Per-agent entries also accept
`api_key_env:` (route a key from a custom variable) and `base_url:` (point a
provider at a proxy or compatible endpoint); GPT/Gemini/Grok/DeepSeek are
served by one stdlib HTTP adapter (no extra packages), while Claude uses the
official SDK (`pip install anthropic`). Model names are operator-editable
defaults.

**Fallback contract.** Backbones are availability-checked when a run starts
(key present, SDK importable) and every live call is guarded: if an agent's
provider is missing, unreachable, or errors mid-call, **that agent alone**
drops to its deterministic offline fallback and the reason is recorded in the
run manifest — the other four agents keep their backbones. With no keys at
all, the shipped config degrades to exactly the offline dry workflow. Every
live call is logged to the manifest with agent, provider, model, tokens, and
cost; the single `cost_cap_usd` is enforced across all backbones per paper.

Other provider modes: `none` (force everything offline), `stub` (replay
recorded fixtures keyed by request fingerprint — tests/CI), or a single
provider name (e.g. `provider: deepseek`) to run every agent on one backbone.

**Agent Skills (SKILL.md).** Each agent has an instruction document in the
open [Agent Skills](https://agentskills.io) format under
[skills/](skills/README.md) — `quant-scout` … `quant-reviewer` — teaching its
backbone the job's conventions (extraction rules, sandbox constraints,
verdict gates). They are consumed two ways, set per agent:

- **`mode: api` (route 2, the default)** — the router prepends the agent's
  skill body to the system prompt of every single-shot call. Works with all
  five providers; no harness needed. Disable globally with `skills_dir: ""`.
- **`mode: harness` (route 1, opt-in, anytime)** — drive a skill-supporting
  agent-host CLI instead of the bare API. Default command is headless Claude
  Code; point `harness_command` at any standard-compliant host
  (`["claude", "-p", "{prompt}", "--model", "{model}"]` — placeholders
  `{prompt}`/`{system}`/`{model}` are substituted). A host missing from PATH
  or a failed invocation falls back offline for that agent like any other
  backbone failure. CLI hosts don't report tokens, so harness calls log zero
  cost — bound them with iteration budgets.

```yaml
    quant_coder:                  # example: flip the coder to route 1
      provider: anthropic
      mode: harness
      harness_command: ["claude", "-p", "{prompt}", "--model", "{model}"]
```

Editing a SKILL.md changes the system prompt and therefore request
fingerprints — re-record stub fixtures for that agent after edits. (These
skill files are unrelated to the runtime plug-ins below; see
[skills/README.md](skills/README.md).)

`quant_scout.charter` defines what research is in scope (purpose, themes,
must-haves, exclusions); when the `charter_relevance` skill is enabled it
dominates the keyword ranking. Note `OPENAI_API_KEY` does double duty: it is
also PaperQA2's default backend for full-text reading, separately from the
reviewer's backbone.

Per-agent skills (all shipped `enabled: false` except `code_generation`,
which is on by default so reports ship a generated strategy module):

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
cleared. Suite totals: **223 tests** (fast suite + `e2e` + `eval` markers);
CRSP-backed cases skip automatically when the data is absent.

### 10. Repository layout

```text
configs/                  agents.yaml (skills + llm + charter), benchmarks.yaml
data/raw|processed/       market data + caches (gitignored)
docs/                     architecture.md, skills-design.md, phase2-design.md, phase2-status.md
runs/                     per-run manifests + artifacts (gitignored)
reports/                  review .md + generated _strategy.py (on by default; gitignored)
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
tests/                    223 tests incl. e2e and eval markers
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
