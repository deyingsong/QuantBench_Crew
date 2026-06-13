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

## Editing

Frontmatter requires `name` and `description` (what the skill is for + when
to use it); the body is plain markdown instructions. Keep bodies tight and
factual — they ride on every LLM call the agent makes, so length is cost.
Because the body lands in the system prompt, editing a skill changes request
fingerprints: recorded stub fixtures for affected agents must be re-recorded.
