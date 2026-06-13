# Coder Skills Design Note

Status: implemented
Date: 2026-06-13
Scope: give the `quant_coder` agent an expert-enhanced open-format skill family,
distilled from the implementation/practitioner transcript corpus and adapted
from a vendored production-engineering skill library, plus a wired cross-agent
"consult the Reader" seam. No change to agent public APIs or the frozen
dataclass discipline.

## Motivation

Of the five pipeline agents, the Coder had the thinnest open-format
(`SKILL.md`) knowledge layer: a single `quant-coder/SKILL.md` stating the
`Strategy`/`PanelData` contract and sandbox rules, with no expert-distilled
references or task sub-skills — while Scout, Reader, Bench, and Reviewer each
had a family. Yet the design (see [skills-design.md](skills-design.md)) calls
the Coder->Bench seam "the pipeline's value." This note records the build that
closes that gap.

## What was built

### 1. Transcript-distilled coder skills (the craft + defense layer)

- **`strategy-implementer/`** — turning a `MethodSpec` into a deterministic,
  leakage-free module: point-in-time discipline, correct indicator
  construction, signal-to-weight recipes, next-bar execution timing, warmup
  handling. Reference: `references/strategy-implementation-craft.md`.
- **`backtest-pitfall-guard/`** — the code-generation-time defense against the
  failure modes that inflate measured performance: look-ahead/parameter
  leakage, survivorship, in-sample tuning, multiple-testing/selection bias
  across generation attempts, and overfitting the reproduction target.
  Reference: `references/backtest-pitfall-discipline.md`.

Both are distilled from the ten requested implementation/practitioner folders
under `Source_data/transcript/` (1,642 substantive transcripts) and carry an
Expert-Lenses table spanning Algovibes, QuantPy, QuantInsti, Luke Finance,
Ernest Chan, Kevin Davey, Predicting Alpha, Lopez de Prado, Jim Simons, and
Victor Niederhoffer. They mirror the granularity of Bench's two and Reviewer's
two task skills.

### 2. Cross-agent oracle: `consult-reader/`

Adapts agent-skills' `interview-me` + `idea-refine` with one substitution: the
Coder consults the **Reader** (which holds the paper), not a human. It detects
performance-affecting `MethodSpec` gaps, forms one hypothesis-carrying question
per gap, and routes them to the Reader for source-grounded answers, adopting a
declared neutral default (recorded as an assumption) only where the source is
silent.

This is wired end to end, not just documented:

- `src/quantbench_crew/skills/coder/consult_reader.py` — `ConsultReaderSkill`
  with deterministic, LLM-free `detect_gaps(...)`; optional resolution through
  the **Reader** backbone (`llm_for_agent(ctx.llm, "quant_reader")`), bounded by
  the shared per-paper cost cap; emits `generated/reader_consultation.json`.
- `QuantCoderAgent.consult_reader(analysis, ctx)` — mirrors `generate` /
  `synthesize_metrics`; returns `None` when the skill is disabled.
- `main.py` calls it after `coder.plan(...)` and before `coder.generate(...)`.
- `configs/agents.yaml` declares `consult_reader` (shipped `enabled: false`,
  `resolve: false`, `confidence_threshold: 0.5`), so default behavior is
  unchanged and the dry workflow stays the baseline.
- `prompts/consult_reader.txt` — the Reader-directed prompt.
- `tests/test_consult_reader_skill.py` — gap detection, offline emission,
  Reader resolution, cost-cap gating, and the agent no-op-when-disabled seam.

Offline-safe: deterministic gap detection needs no LLM; with no Reader backbone
the skill emits questions for a harness re-invocation or a human and never
fabricates answers.

### 3. Adapted engineering reskins

Six `coder-*` skills reskin the coder-relevant production-engineering skills for
strategy codegen, each pointing back to its vendored original:
`coder-source-grounding`, `coder-doubt-driven`, `coder-test-first`,
`coder-incremental-implementation`, `coder-debugging-recovery`,
`coder-self-review`.

### 4. Vendored engineering library

`skills/engineering/` is a verbatim, MIT-licensed copy of
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (commit
`d187883`, 2026-06-10) — all 24 skills, the 4 agent personas, the 5 checklists,
and the skill-anatomy doc — kept intact for attribution and re-sync. Host-
specific automation (hooks/commands) is intentionally not vendored.

## How they are consumed

Unchanged from the existing model (see [../skills/README.md](../skills/README.md)):

- **Route 2 (default, `mode: api`).** `quant-coder/SKILL.md` carries the
  family's core rules (a "Coder skill family" + "Before you emit" section), so
  every single-shot coder call gets them injected. `agent_skills.py` still maps
  `quant_coder -> quant-coder` only; the sub-skills are not separate injection
  targets, exactly as the Reader/Bench sub-skills are not.
- **Route 1 (`mode: harness`).** A standard-compliant host discovers every
  `skills/*/SKILL.md` natively, including the new coder family and the vendored
  library.

## Risk notes

- Editing `quant-coder/SKILL.md` changes the coder's route-2 request
  fingerprint. The codegen tests set `ctx.llm` directly (bypassing skill
  injection), so they are unaffected; the full suite stays green (323 passed).
  Any future recorded coder fixtures built through the skill-augmented client
  must be re-recorded after edits.
- `consult_reader` ships disabled, so the default manifest and e2e hashes are
  unchanged; enabling it adds one skill record and the consultation artifact.
