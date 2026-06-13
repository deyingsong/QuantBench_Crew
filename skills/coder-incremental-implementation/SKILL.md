---
name: coder-incremental-implementation
description: Build a strategy module in thin, runnable vertical slices (warmup -> feature -> signal -> weights -> invariants) rather than all at once, keeping the candidate sandbox-runnable at every step. Use when implementing a non-trivial strategy, when the signal has several stages, or when a single large emission would be hard to debug if a template test fails.
---

# Coder Incremental Implementation

Adapted for the QuantBench Coder from agent-skills
[incremental-implementation](../engineering/skills/incremental-implementation/SKILL.md).
Its vertical-slice discipline maps onto the strategy pipeline: build one stage
at a time, keep the module runnable in the sandbox after each, so a failing
template test localizes to the slice you just added.

## Overview

A strategy emitted in one shot that fails the no-lookahead test gives you no
localization. Slicing the pipeline turns one opaque failure into a sequence of
small, attributable ones.

## When to Use

- The signal has multiple stages (feature, rank, construction, sizing).
- A one-shot emission would be hard to debug on failure.

**Not for** a trivial one-line signal where a single emission is clearest.

## The Increment Cycle

Pick the thinnest slice that keeps the module valid, implement it, run the
template tests in the sandbox, then add the next slice.

### Preferred slicing order (vertical, contract-first)

1. **Skeleton** — `build_strategy` returning an object with `fit`/`weights`
   that returns `{}` (passes shape during warmup; nothing leaks).
2. **Point-in-time read** — `weights` reads only `data.up_to(as_of)`.
3. **Feature** — compute the trailing signal from history, warmup-guarded.
4. **Construction** — map signal to target weights under the spec's rule.
5. **Invariants** — enforce net/gross/leg constraints; re-check after clipping.

## Implementation Rules

- **Rule 0 — Simplicity first.** The simplest slice that holds the contract.
- **Rule 1 — One stage at a time.** Don't add construction while the feature is
  still unverified.
- **Rule 2 — Keep it runnable.** Every slice must execute in the sandbox; a
  half-written feature returns `{}` rather than crashing.
- **Rule 3 — Safe default is `{}`.** Any not-yet-implemented branch returns no
  position, never a guessed one.
- **Rule 4 — Rollback-friendly.** If a slice regresses the score, drop just
  that slice, not the whole module.

## Red Flags

- Emitting the full module before any slice has run in the sandbox.
- A slice that crashes instead of degrading to `{}`.
- Adding the next stage while the current one fails a template test.

## Verification

- [ ] The module ran in the sandbox after each slice, not only at the end.
- [ ] Unimplemented branches return `{}`, never a guessed position.
- [ ] A failing template test localizes to a single slice.
