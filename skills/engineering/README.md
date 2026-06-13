# Engineering Skills Library (vendored)

This directory is a **verbatim, unmodified copy** of the production-grade
engineering skills from
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
reproduced here under its MIT license (see [LICENSE](LICENSE)).

- **Upstream commit:** `d187883b7d761265309cdcc0f202cc76b4b3fb06`
- **Upstream date:** 2026-06-10
- **Author:** Addy Osmani — Copyright (c) 2025, MIT License.

Nothing in this folder is QuantBench-specific. It is a general software-
engineering skill library kept intact so it can be re-synced from upstream and
so attribution stays clean. The QuantBench-specific *adaptations* of these
skills live one level up as first-class skills (see below).

## What is here

| Path | Contents |
| --- | --- |
| `skills/` | All 24 upstream skills, one folder per skill, each with its `SKILL.md` (plus any supporting files/scripts). |
| `agents/` | The 4 upstream specialist review personas (code-reviewer, security-auditor, test-engineer, web-performance-auditor). |
| `references/` | The 5 upstream checklists (accessibility, orchestration, performance, security, testing). |
| `docs/skill-anatomy.md` | The upstream description of the SKILL.md format. |

Host-specific automation from upstream (`hooks/`, `commands/`, `.claude/`,
`.gemini/`, `.opencode/`) is intentionally **not** vendored, so this repo
introduces no executable session hooks or slash commands. Pull them from
upstream directly if a host needs them.

## The 24 skills, by lifecycle phase

- **DEFINE** — `interview-me`, `idea-refine`, `spec-driven-development`
- **PLAN** — `planning-and-task-breakdown`
- **BUILD** — `incremental-implementation`, `test-driven-development`,
  `context-engineering`, `source-driven-development`,
  `doubt-driven-development`, `frontend-ui-engineering`,
  `api-and-interface-design`
- **VERIFY** — `browser-testing-with-devtools`, `debugging-and-error-recovery`
- **REVIEW** — `code-review-and-quality`, `code-simplification`,
  `security-and-hardening`, `performance-optimization`
- **SHIP** — `git-workflow-and-versioning`, `ci-cd-and-automation`,
  `deprecation-and-migration`, `documentation-and-adrs`,
  `observability-and-instrumentation`, `shipping-and-launch`
- **META** — `using-agent-skills`

## How QuantBench uses this library

The `coder` agent (`quant_coder`) does one job: turn an extracted `MethodSpec`
into a deterministic, leakage-free Python strategy module that satisfies the
`Strategy` / `PanelData` contract and is scored by sandboxed template tests.
A handful of these upstream skills map directly onto that job; the repo ships
**QuantBench-adapted reskins** of them as first-class skills so the coder's
backbone gets quant-specific guidance (the `Strategy` contract, the sandbox
allowlist, point-in-time data, the paper's claims) instead of generic web-app
advice:

| Vendored upstream skill | QuantBench reskin (first-class) |
| --- | --- |
| `interview-me` + `idea-refine` | [`consult-reader`](../consult-reader/) — consult the Reader agent, not a human, to close spec gaps |
| `source-driven-development` | [`coder-source-grounding`](../coder-source-grounding/) |
| `doubt-driven-development` | [`coder-doubt-driven`](../coder-doubt-driven/) |
| `test-driven-development` | [`coder-test-first`](../coder-test-first/) |
| `incremental-implementation` | [`coder-incremental-implementation`](../coder-incremental-implementation/) |
| `debugging-and-error-recovery` | [`coder-debugging-recovery`](../coder-debugging-recovery/) |
| `code-review-and-quality` | [`coder-self-review`](../coder-self-review/) |

The reskins carry the same workflow spine as their upstream source and link
back to it here for the full generic treatment. The remaining upstream skills
(shipping, CI/CD, frontend, browser testing, observability, deprecation, …)
are not in the coder's hot path but are kept intact for any agent host that
wants them through native skill discovery.

See [../README.md](../README.md) for how all skills are consumed (route 2
prompt injection vs. route 1 harness discovery).
