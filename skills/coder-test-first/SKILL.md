---
name: coder-test-first
description: Anticipate and satisfy the deterministic template tests (shape, determinism, no-lookahead, construction invariants) before and while writing a strategy module, treating them as the executable spec the candidate is scored against. Use when generating or revising a candidate, when a template test fails in the sandbox, or when deciding what behavior the module must guarantee.
---

# Coder Test-First

Adapted for the QuantBench Coder from agent-skills
[test-driven-development](../engineering/skills/test-driven-development/SKILL.md).
The Red-Green-Refactor cycle maps directly onto the Coder->Bench seam: the
**template tests already exist** (shape, determinism, no-lookahead, and the
spec's construction invariants), the sandbox runs them, and `execute_fn` scores
on how many pass. Treat them as the failing test you write to first.

## Overview

The candidate's score is tests-passed plus a structure prior. So the tests are
not an afterthought — they are the target. Write the module to make the
no-lookahead and determinism tests pass *by construction*, not by retrofitting.

## When to Use

- Generating a new candidate, or revising one after a sandbox failure.
- Deciding what guarantees the `weights(...)` method must hold.

## The Cycle

### RED — read the tests as the spec

Before writing logic, restate what the four template checks demand for this
spec: a non-empty dict of finite floats once warm and `{}` during warmup
(shape); identical output for identical `(data, params)` (determinism);
weights at `t` unchanged when data after `t` changes (no-lookahead); plus the
spec's construction invariants (net ~0 for long-short, uniform leg magnitudes,
gross `<= 2x`).

### GREEN — implement to pass by construction

Write the simplest `weights` that satisfies them: read only `data.up_to(as_of)`,
return `{}` before warmup, seed randomness from params. Passing no-lookahead
comes from the point-in-time read, not from a post-hoc patch.

### REFACTOR — simplify without breaking green

Once the sandbox shows all template tests pass, simplify the implementation
(clarity over cleverness) and re-run; never refactor away the point-in-time
discipline.

### The prove-it pattern (failures)

When a template test fails, do not guess-edit. Reproduce the exact failure from
the candidates record, identify which guarantee broke, and fix that — a
no-lookahead failure means a future read leaked in; find and remove it.

## Spec-Specific Tests

Beyond the templates, anticipate edge cases the *signal formula* implies:
sample-period boundaries, a single eligible asset, all-equal inputs, a missing
field mid-history. Make the module behave sanely (usually `{}`), since these
are where a faithful-looking module breaks.

## Red Flags

- Writing the module first and hoping the no-lookahead test passes.
- Patching a determinism failure by removing a symptom instead of the global
  state or time dependency causing it.
- Treating a green template run as proof of validity (see
  [backtest-pitfall-guard](../backtest-pitfall-guard/SKILL.md)).

## Verification

- [ ] The module passes shape, determinism, no-lookahead, and construction
  tests in the sandbox.
- [ ] No-lookahead passes by point-in-time construction, not retrofit.
- [ ] Edge cases implied by the signal formula were considered.
