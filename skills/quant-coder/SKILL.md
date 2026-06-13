---
name: quant-coder
description: Write deterministic, sandbox-safe Python strategy modules implementing the QuantBench Strategy contract against the PanelData API. Use when generating or revising candidate trading-strategy code for a paper reproduction.
---

# QuantCoder: strategy module conventions

You write small, self-contained Python modules that run inside a locked-down
sandbox and are scored by deterministic template tests before any benchmark
sees them. Code that violates the conventions below scores zero — correctness
of intent does not rescue a sandbox violation.

## The contract

The module must define `build_strategy(params=None)` returning an object with:

- `fit(data, train_end)` — estimate anything needed using data up to
  `train_end` only.
- `weights(data, as_of)` — return `dict[asset_id, float]` using ONLY
  information at dates <= `as_of`. Call `data.up_to(as_of)` defensively
  before reading anything.

`params` may contain `formation_periods`, `skip_periods`, `fraction`,
`field`; respect them with sensible defaults.

## The PanelData API (the only data surface)

- `data.dates()` -> sorted tuple of `datetime.date`
- `data.assets()` -> sorted tuple of asset-id strings
- `data.value(as_of, asset, field, default=None)` -> float or default
- `data.history(asset, field, end, periods)` -> last `periods` values at
  dates <= end
- `data.up_to(as_of)` -> the same panel truncated to dates <= `as_of`

## Sandbox rules (violations are rejected before execution)

- Imports allowed ONLY from: math, statistics, random, datetime, itertools,
  functools, collections, json, typing, dataclasses, operator, bisect, heapq.
- Banned everywhere: eval/exec/compile/open/input/getattr/setattr/delattr/
  globals/locals/vars, `__import__`, any dunder attribute access, file or
  network access, `if __name__ == "__main__"` blocks.
- numpy/pandas/sklearn are available only when the operator enables the
  numeric sandbox tier — assume stdlib-only unless told otherwise.

## Hard behavioral requirements (the template tests)

1. **Determinism** — identical data and params must produce identical
   weights. Seed any randomness from params; never from time or global state.
2. **No lookahead** — weights at `t` must not change when data after `t`
   changes. This is tested by mutation; internal `up_to(as_of)` discipline is
   how you pass.
3. **Shape** — weights are a non-empty dict of finite floats over known
   assets once enough history exists; return `{}` during warmup.
4. **Construction invariants** — long-short specs must produce ~zero net
   weight; equal-weight legs must have uniform magnitudes; gross exposure
   stays <= 2x.

## Coder skill family

This SKILL.md is the contract. The craft, defenses, and gap-handling live in
companion skills a harness discovers natively and whose core rules apply on
every generation:

- **[strategy-implementer](../strategy-implementer/SKILL.md)** — build features
  from past data only, map the signal to weights under the construction rule,
  time trades to the next bar, handle warmup with `{}`.
- **[backtest-pitfall-guard](../backtest-pitfall-guard/SKILL.md)** — before
  accepting a candidate, sweep for look-ahead and parameter leakage,
  survivorship, in-sample tuning, and overfitting to the paper's claimed
  number; record every trial.
- **[consult-reader](../consult-reader/SKILL.md)** — when a performance-affecting
  field is missing, vague, or low-confidence, ask the Reader instead of
  guessing; adopt a neutral default only as a recorded assumption.
- **coder-source-grounding / -doubt-driven / -test-first /
  -incremental-implementation / -debugging-recovery / -self-review** — adapted
  software-engineering discipline (see [engineering/](../engineering/README.md)).

## Before you emit

1. Point-in-time: every read goes through `data.up_to(as_of)`; nothing dated
   after `as_of` is read or inferred.
2. Estimated parameters are fit in `fit(...)` on `<= train_end` and frozen.
3. Warmup returns `{}`; any randomness is seeded from `params`.
4. No performance-affecting field was silently guessed; gaps went to
   consult-reader and adopted defaults are recorded as assumptions.
5. The code implements the method, not the paper's claimed metric.

Output only the module source. Prefer the simplest faithful implementation of
the extracted MethodSpec over cleverness.
