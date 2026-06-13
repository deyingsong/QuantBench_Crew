---
name: coder-self-review
description: Run a five-axis self-review of a generated strategy module before emitting it — correctness against the spec, readability, contract/architecture conformance, sandbox safety, and no-lookahead/leakage — and categorize findings by severity. Use as the final gate before accepting a candidate, after the template tests pass, or when reviewing a module written by another agent or adapter.
---

# Coder Self-Review

Adapted for the QuantBench Coder from agent-skills
[code-review-and-quality](../engineering/skills/code-review-and-quality/SKILL.md),
keeping its five-axis review and severity categorization, re-aimed at a single
strategy module. A passing template run is the entry condition for this review,
not a substitute for it.

## Overview

The template tests prove mechanical correctness; they do not prove the module
*faithfully implements the spec* or is free of conceptual leakage. This review
is the last cheap chance to catch that before the Bench scores the artifact.

## When to Use

- Final gate before accepting a candidate (after template tests pass).
- Reviewing a module produced by the agent adapter or another model.

## The Five-Axis Review

### 1. Correctness vs the spec

Does the module implement the `MethodSpec` signal, construction, frequency, and
sample faithfully? Any silent deviation, any field implemented by guess?

### 2. Readability & simplicity

Is the `weights` method obviously correct on inspection? Prefer a plain loop
whose timing is verifiable over a clever vectorized form that hides it.

### 3. Contract & architecture

`build_strategy(params=None)` present; `fit`/`weights` shaped per contract;
`params` respected with sensible defaults; no module-level mutable state.

### 4. Sandbox safety

Imports within the allowlist; no eval/exec/open/network/dunder access; no
`__main__` block. (These are the Coder's real "security" axis.)

### 5. No-lookahead & leakage

The decisive axis: does every feature, rank, and fill use data `<= as_of`? Are
estimated parameters frozen out-of-sample? Is the universe point-in-time? Hand
the deeper sweep to [backtest-pitfall-guard](../backtest-pitfall-guard/SKILL.md).

## Categorize Findings

- **Blocker** — leakage, sandbox violation, or spec infidelity. Do not emit;
  fix or route to [consult-reader](../consult-reader/SKILL.md).
- **Major** — construction-invariant risk, fragile timing. Fix before emit.
- **Minor** — readability, naming. Note; optional.

Emit only when no blocker remains.

## Red Flags

- Treating a green template run as a finished review.
- Passing over a silent spec deviation because the code "looks clean".
- Emitting with an unresolved leakage or sandbox finding.

## Verification

- [ ] All five axes were checked, with no-lookahead checked last and hardest.
- [ ] Findings were categorized; no blocker remains at emit.
- [ ] Spec infidelities were fixed or routed, not waved through.
