# Agent Skills

Instruction documents in the open [Agent Skills](https://agentskills.io)
SKILL.md format — one per pipeline agent — teaching each agent's LLM backbone
how to do its job in this repository.

> **Naming note:** these are *not* the runtime plug-ins in
> `src/quantbench_crew/skills/` (Python capabilities with `run()` methods).
> Same word, different concept: SKILL.md files are knowledge for models;
> the plug-ins are executable pipeline steps.

## How they are consumed

| Route | Mode | Mechanism |
| --- | --- | --- |
| 2 (default) | `mode: api` | The per-agent LLM router prepends the agent's skill body to the system prompt of every single-shot call (`llm.skills_dir` in `configs/agents.yaml`; set it empty to disable). |
| 1 (optional) | `mode: harness` | The same composed prompt rides into an agent-host CLI (Claude Code by default; any standard-compliant host via `harness_command`). Hosts that support the standard can also discover these files natively. |

Skill-to-agent mapping lives in `quantbench_crew/agent_skills.py`
(`quant_scout -> quant-scout/`, etc.). A missing SKILL.md disables injection
for that agent only — nothing errors.

Scout also has two task-focused open-format skills:
`new-paper-tracker/` for date-window surveillance and durable queue updates,
and `relevance-scorer/` for transcript-distilled research-value ranking.
Harnesses can discover them natively; `quant-scout/` carries their core rules
for the default prompt-injection route.

Reader has four task-focused open-format skills:
`question-identifier/`, `methodology-extractor/`, `empirical-spec-parser/`,
and `criticizer/`. They distill the academic/research transcript corpus into
separate source-grounded workflows. Harnesses can discover them natively;
`quant-reader/` carries their core rules for the default prompt-injection
route.

Bench has two task-focused open-format skills:
`strategy-evaluator/` for transcript-distilled multi-dataset and baseline
evaluation, and `robustness-auditor/` for stress testing and experiment
provenance. Harnesses can discover them natively; `quant-bench/` carries their
core rules for the default prompt-injection route.

Reviewer has two task-focused open-format skills:
`claims-vs-results-analyzer/` for forensic claim comparison and reproducibility
diagnosis, and `report-compiler/` for comprehensive evidence-linked Markdown
reviews through explicit quantitative expert lenses. Harnesses can discover
them natively; `quant-reviewer/` carries their core rules for the default
prompt-injection route.

Coder has a craft-and-defense skill family, a cross-agent oracle, and adapted
engineering discipline. Two transcript-distilled skills do the core work:
`strategy-implementer/` for turning a MethodSpec into deterministic,
leakage-free code against the Strategy/PanelData contract, and
`backtest-pitfall-guard/` for catching look-ahead, overfitting, and selection
bias at generation time. `consult-reader/` lets the Coder close MethodSpec gaps
by asking the Reader agent instead of guessing — the cross-agent adaptation of
agent-skills' `interview-me`/`idea-refine`, wired through the `consult_reader`
Python skill and `QuantCoderAgent.consult_reader`. Six reskins
(`coder-source-grounding/`, `coder-doubt-driven/`, `coder-test-first/`,
`coder-incremental-implementation/`, `coder-debugging-recovery/`,
`coder-self-review/`) adapt the production-engineering skills for strategy
codegen. Harnesses can discover them natively; `quant-coder/` carries their
core rules for the default prompt-injection route.

`options-reader/` is a cross-agent domain-expert skill for equity-derivatives
pricing, volatility surfaces, exotics, and hedging. Scout should identify and
route papers whose central contribution falls in this domain; Reader or
Reviewer can then invoke the skill for source-grounded extraction or
adversarial domain critique. It is progressively disclosed through native
skill discovery and is not injected into unrelated default API calls.

`microstructure-reader/` is a cross-agent domain-expert skill for HFT,
tick-data, market-making, market-impact, execution, liquidity, and venue-design
research. Scout should identify and route papers whose central contribution
falls in this domain; Reader or Reviewer can then invoke the skill for
source-grounded extraction or adversarial domain critique. It is progressively
disclosed through native skill discovery and is not injected into unrelated
default API calls.

`macro-and-rates-reader/` is a cross-agent domain-expert skill for fixed-income,
macroeconomic, monetary-policy, yield-curve, and rates-strategy research. Scout
should identify and route papers whose central contribution falls in this
domain; Reader or Reviewer can then invoke the skill for source-grounded
extraction or adversarial domain critique. It is progressively disclosed
through native skill discovery and is not injected into unrelated default API
calls.

`factor-reader/` is a cross-agent domain-expert skill for cross-sectional
equity factors, anomalies, characteristic portfolios, factor-model alpha, and
post-publication decay. Scout should identify and route papers whose central
contribution falls in this domain; Reader or Reviewer can then invoke the skill
for source-grounded extraction or adversarial domain critique. It is
progressively disclosed through native skill discovery and is not injected
into unrelated default API calls.

## Vendored engineering library

`engineering/` is a verbatim, MIT-licensed copy of
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — 24
production-grade software-engineering skills plus its specialist agent personas
and checklists, kept intact for attribution and re-sync (see
[engineering/README.md](engineering/README.md)). The QuantBench-specific
adaptations of the coder-relevant subset live as the `coder-*` and
`consult-reader` skills above; the rest of the library is available to any
standard-compliant agent host through native skill discovery but is not
injected into default API calls.

## Editing

Frontmatter requires `name` and `description` (what the skill is for + when
to use it); the body is plain markdown instructions. Keep bodies tight and
factual — they ride on every LLM call the agent makes, so length is cost.
Because the body lands in the system prompt, editing a skill changes request
fingerprints: recorded stub fixtures for affected agents must be re-recorded.
