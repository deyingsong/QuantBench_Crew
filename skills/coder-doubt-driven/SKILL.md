---
name: coder-doubt-driven
description: Subject a trusted-looking MethodSpec interpretation to a short adversarial review before writing code against it. Use when the spec looks complete but the method is unfamiliar or high-stakes, when a single reading is about to drive a whole implementation, or when correctness of the interpretation matters more than speed.
---

# Coder Doubt-Driven Development

Adapted for the QuantBench Coder from agent-skills
[doubt-driven-development](../engineering/skills/doubt-driven-development/SKILL.md),
preserving its CLAIM → EXTRACT → DOUBT → RECONCILE → STOP loop. The artifact
under review is not a code diff but **the interpretation of the method** you are
about to implement.

## Overview

The dangerous spec is not the obviously-vague one (consult-reader catches that)
— it is the one that *looks* complete, so you implement a single reading without
noticing the alternative readings that change the result.

## When to Use

- The spec reads as complete but the method is unfamiliar or consequential.
- One interpretation is about to drive the entire module.
- A wrong reading would be expensive to discover only after the Bench runs.

**Not for** trivial specs or cosmetic choices.

## The Process

### 1. CLAIM — surface what stands

State, in one or two lines, the interpretation you are about to commit to:
"This signal is 12-1 momentum, value-weighted deciles, monthly, non-overlapping."

### 2. EXTRACT — smallest reviewable unit

Reduce it to the specific, falsifiable decisions: window = 12, skip = 1,
weighting = value, legs = top/bottom decile, holding = 1 month non-overlapping.

### 3. DOUBT — argue the alternative readings

For each decision, name the plausible alternative and what it would do to the
weights: equal- vs value-weight changes leg construction; overlapping vs
non-overlapping changes turnover; skip-month present vs absent shifts the
signal. Ask whether the paper actually disambiguates each, or you assumed it.

### 4. RECONCILE — fold findings back

Where the doubt found a genuine ambiguity that affects performance, send it to
[consult-reader](../consult-reader/SKILL.md). Where the paper does disambiguate,
record the citation and proceed.

### 5. STOP — bounded, not recursive

One adversarial pass per interpretation. The goal is to catch the
silently-assumed reading, not to loop forever; stop when the remaining
ambiguities are either resolved or routed.

## Red Flags

- Implementing a complete-looking spec without naming a single alternative reading.
- Treating "the spec looks fine" as evidence that it is unambiguous.
- Looping the doubt pass instead of routing real gaps to the Reader.

## Verification

- [ ] The committed interpretation was stated explicitly before coding.
- [ ] Each performance-affecting decision was checked against its alternative.
- [ ] Genuine ambiguities were routed to consult-reader; resolved ones cited.
