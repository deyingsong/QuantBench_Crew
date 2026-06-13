---
name: consult-reader
description: Close gaps in an extracted MethodSpec by consulting the Reader agent (which holds the paper) instead of guessing. Detects under-specified or low-confidence spec fields, forms one hypothesis-carrying question per gap grounded in the spec, and routes them to the Reader for source-grounded answers before code is written. Use when the MethodSpec is missing or vague on universe, signal, construction, frequency, or sample; when extraction_confidence is low; or whenever you catch yourself about to silently fill an ambiguous requirement that would change measured performance.
---

# Consult Reader

Adapted for the QuantBench pipeline from the agent-skills `interview-me` and
`idea-refine` skills (see [../engineering/skills/interview-me/SKILL.md](../engineering/skills/interview-me/SKILL.md)
and [../engineering/skills/idea-refine/SKILL.md](../engineering/skills/idea-refine/SKILL.md)).
The adaptation is one substitution with large consequences: the Coder does not
interview a human, it **consults the Reader agent**, which holds the paper and
produced the `MethodSpec`. The Reader is the oracle; the paper is ground truth.

## Overview

What the spec says and what the method actually requires are often different.
A `MethodSpec` field can be empty, vague ("monthly-ish"), or low-confidence,
and the cheapest moment to resolve that gap is *before* code exists — after you
have started implementing, a wrong guess gets locked into the artifact the
Bench then scores, silently inflating or deflating the result.

This skill closes the gap by asking the Reader one focused, hypothesis-carrying
question per gap, grounded in the spec, until you can implement without guessing
on anything that affects measured performance.

## When to Use

Apply when the spec leaves a *performance-affecting* decision underspecified:

- a required field (universe, frequency, signal_definition,
  portfolio_construction, rebalance_frequency, holding_period) is empty or
  contains a vague/placeholder marker;
- `extraction_confidence` is low, or the field carries no supporting evidence;
- two reasonable interpretations of the signal would produce materially
  different weights;
- you are about to pick the interpretation that happens to match the paper's
  headline number (that is a reason to ask, not to proceed).

**When NOT to use:**

- the spec is complete and unambiguous on every performance-affecting field;
- the gap is cosmetic and cannot change weights (variable naming, comments);
- a deterministic default is explicitly sanctioned by the spec.

## The Process

### 1. Hypothesize, with a confidence number

For each gap, write your best reading of the field in one line plus an honest
confidence (0–100%). Below ~70%, append what is unresolved. The number forces
honesty: if you cannot predict the Reader's answer, the number is low.

### 2. Ask one question per gap, each with your guess attached

Format each as a question the Reader can answer from the paper:

```
Q:     <one focused question about a specific spec field>
GUESS: <your default interpretation and the reasoning behind it>
```

Attaching the guess lets the Reader confirm or correct faster than answering
from scratch, and commits you to a falsifiable interpretation. Prefer the
guess grounded in the spec's evidence, not the one that flatters the result.

### 3. Demand source-grounded answers

The Reader must answer from the paper, not from plausibility. An acceptable
answer cites the paper (section, table, equation) or explicitly says
"unspecified in source." "Unspecified in source" is a real, useful answer — it
tells you to fall back to a declared, neutral default and record the
assumption, rather than to a flattering guess.

### 4. Restate the resolved spec and stop

When every performance-affecting gap is resolved or explicitly defaulted, write
back the now-implementable interpretation per field, and record any
"unspecified in source" defaults as assumptions on the artifact. Stop
consulting when you can implement without guessing — not before, and not after.

## Output

A `reader_consultation` record (the [consult-reader Python skill](../../src/quantbench_crew/skills/coder/consult_reader.py)
emits it to `generated/reader_consultation.json`) containing:

- `gaps`: each underspecified field, its issue, and your hypothesis;
- `questions`: the Reader-directed questions, one per gap;
- `answers`: the Reader's source-grounded answers when resolution ran;
- `assumptions`: defaults adopted where the source was silent;
- `consulted`: which backbone answered (`quant_reader`) or `none` (offline:
  questions emitted for a human/harness to route).

Offline-safe: with no Reader backbone available the skill still emits the gaps,
questions, and hypotheses so a harness re-invocation or a human can resolve
them; it never fabricates answers.

## Interaction with Other Skills

- **[strategy-implementer](../strategy-implementer/SKILL.md)**: downstream.
  Consult-reader resolves the gaps; strategy-implementer writes the code
  against the resolved spec.
- **[backtest-pitfall-guard](../backtest-pitfall-guard/SKILL.md)**: sibling. The
  guard sends a gap here rather than choosing the flattering interpretation.
- **[coder-doubt-driven](../coder-doubt-driven/SKILL.md)**: complementary.
  Doubt-driven stress-tests the spec you already trust; consult-reader resolves
  the parts you cannot yet trust.

## Red Flags

- Filling a performance-affecting field by guess instead of asking the Reader.
- A question without an attached hypothesis (surveying, not committing).
- Accepting a plausibility answer with no paper citation as if it were grounded.
- Choosing the interpretation that matches the headline number because it is
  convenient.
- Running this in a non-interactive context with no Reader backbone and then
  proceeding anyway instead of emitting the questions as a blocker.

## Verification

- [ ] Every performance-affecting gap got a hypothesis with a confidence number.
- [ ] One Reader-directed question per gap, each carrying the Coder's guess.
- [ ] Answers are source-grounded (cite the paper) or explicitly "unspecified".
- [ ] Defaults adopted where the source was silent are recorded as assumptions.
- [ ] No performance-affecting field was silently guessed.
