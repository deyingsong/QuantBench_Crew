---
name: strategy-implementer
description: Translate an extracted MethodSpec into a deterministic, leakage-free Python strategy module that satisfies the QuantBench Strategy/PanelData contract, applying quant-practitioner implementation craft — point-in-time discipline, correct indicator construction, signal-to-position translation, next-bar execution timing, warmup handling, and in-code transaction costs. Use when the Coder is generating or revising a candidate strategy module, when a signal definition must become executable code, or when deciding how to construct positions, time trades, or handle warmup and missing data without looking ahead.
---

# Strategy Implementer

You convert a `MethodSpec` into a small, self-contained Python module that runs
in the locked-down sandbox, satisfies the `Strategy` contract, and is scored by
deterministic template tests before any benchmark sees it. This skill is the
implementation *craft* layer on top of [quant-coder](../quant-coder/SKILL.md)
(the contract and sandbox rules); read that for the hard interface, read this
for how practitioners get the implementation right.

The governing fact, distilled from hundreds of practitioner walkthroughs: most
strategy bugs are not logic errors, they are **timing and construction errors**
that silently leak the future into the past. Correct intent does not rescue a
look-ahead bug — the no-lookahead template test fails it, and the bench would
have over-reported the edge.

## When to Use

Use when implementing or revising the module that `build_strategy(params=None)`
returns — specifically when you must:

- turn a `signal_definition` (formula or pseudocode) into `weights(...)`;
- decide indicator windows, warmup length, and rolling/EWM construction;
- translate a raw signal into target weights under a construction rule;
- decide execution timing (when a close-based signal may actually trade);
- handle missing data, delistings, or insufficient history.

Do not use for evaluating a finished strategy (that is Bench's
[strategy-evaluator](../strategy-evaluator/SKILL.md)) or for the pre-emit
pitfall sweep (see [backtest-pitfall-guard](../backtest-pitfall-guard/SKILL.md)).

## Reference Router

Load [references/strategy-implementation-craft.md](references/strategy-implementation-craft.md)
for the full distilled craft: the indicator-construction traps, the next-bar
execution rule, the signal-to-weight recipes, and the expert-lens checklist.
Load it whenever the spec involves moving averages, crossovers, z-scores,
ranks, mean-reversion bands, or any rolling-window feature.

## The Implementation Workflow

### 1. Read the spec as a pipeline, not a formula

Decompose the `MethodSpec` into the stages every strategy shares:
`universe -> feature/signal -> target positions -> rebalance schedule ->
costs/holding`. Name the stage each spec field feeds. Missing or vague fields
are gaps — do not silently invent them; flag them for
[consult-reader](../consult-reader/SKILL.md).

### 2. Establish the point-in-time boundary first

Before reading anything, call `data.up_to(as_of)` and read only from that view.
Every feature, rank, and position at time `t` must be computable from data at
dates `<= t`. This is the single discipline that passes the no-lookahead test;
write it first, not last.

### 3. Construct features from past data only

- Use trailing windows (`data.history(asset, field, end=as_of, periods=n)`),
  never centered or forward-filled-from-the-future windows.
- Account for **warmup**: a window of `n` needs `n` prior observations. Until
  they exist, the feature is undefined — return `{}` (no position), do not
  pad with zeros that the comparison logic will misread.
- Exponential/rolling means must consume only history up to `as_of`. The
  classic bug is computing an indicator over the whole series once and then
  indexing it at `t` — that leaks later data into the smoother's state.

### 4. Translate the signal into target weights

Apply the spec's construction rule explicitly and preserve its invariants:

- long-short specs must net to ~zero weight;
- equal-weight legs must have uniform magnitudes;
- gross exposure stays `<= 2x`;
- rank/decile specs select on the cross-section available *at `as_of`*, not on
  the full-period ranking.

### 5. Time the trade honestly

A signal computed from the close of bar `t` cannot transact at that same close.
The practitioner rule (shown explicitly in the Algovibes backtests): a
close-based signal acts at the **next** bar. In this contract you express that
by computing `weights(as_of)` from information `<= as_of` and letting the
harness apply them forward — so never read a price at `as_of` that you could
not have traded at, and never peek one bar ahead to "confirm" a fill.

### 6. Make it deterministic

Identical `(data, params)` must yield identical weights. Seed any randomness
from `params`, never from wall-clock time or global state. No module-level
mutable accumulators that survive across calls.

### 7. Self-check before emitting

Mentally run the four template checks — determinism, no-lookahead (would
weights at `t` change if data after `t` changed?), shape (non-empty dict of
finite floats once warm; `{}` during warmup), and construction invariants.
Only then emit the module source.

## Indicator & Timing Diagnostics

- Does any feature read `data.value(d, ...)` for `d > as_of`? That is leakage.
- Does the warmup branch return `{}` rather than a degenerate all-equal weight?
- Are crossovers compared against the *prior* value using past data only, and
  is the first comparable bar offset past the warmup region?
- Does the position rule re-rank the cross-section at each `as_of`?
- Is net/gross exposure recomputed after any clipping or dropping of assets?
- Are costs/turnover left to the bench, or did the spec ask you to model them
  in-strategy? Default: positions only; let Bench apply the cost model.

## Output Discipline

Output only the module source (no prose, no `__main__` block). Prefer the
simplest faithful implementation of the extracted spec over cleverness — a
plain, obviously-correct `weights` method beats a vectorized one-liner whose
timing is hard to verify.

## Guardrails

- Imports only from the sandbox allowlist (see quant-coder); assume stdlib-only
  unless the numeric tier is explicitly enabled.
- Never read, infer, or "confirm" any value at a date after `as_of`.
- Do not return positions during warmup; return `{}`.
- Do not encode the paper's *claimed result* into the code (e.g. hard-coded
  return paths). Implement the method; let the bench measure it.
- Do not issue investment advice.
