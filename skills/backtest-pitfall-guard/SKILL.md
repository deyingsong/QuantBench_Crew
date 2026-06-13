---
name: backtest-pitfall-guard
description: Guard generated strategy code against the backtest failure modes that inflate apparent performance — look-ahead and leakage, survivorship and point-in-time errors, in-sample parameter tuning, multiple-testing and selection bias across generation attempts, and overfitting to the reproduction target. Use at code-generation time before emitting or accepting a candidate strategy module, when choosing how to estimate parameters, when the generate-test-fix loop iterates on a candidate, or whenever a tempting shortcut would make the backtest look better without making the method more faithful.
---

# Backtest Pitfall Guard

You are the Coder's pre-emit conscience. Generating code that *passes the
template tests* is necessary but not sufficient: a module can be sandbox-clean
and still be quietly overfit, leaky, or tuned to the paper's claimed number.
This skill is the defensive checklist that keeps the Coder->Bench seam honest,
distilled from the practitioners and researchers who specialize in why
backtests lie.

The organizing fact (Lopez de Prado): in finance the signal-to-noise ratio is
low, so a result is *more likely overfit than real*. Your job is to make the
generated code hard to overfit, and to surface — never hide — the choices that
would inflate it.

## When to Use

Use at generation time, before emitting or accepting a candidate, and on every
iteration of the generate-test-fix loop, specifically when:

- deciding how/where to estimate parameters or hyperparameters;
- the loop is about to change code in response to a score;
- a shortcut would improve the apparent backtest (peeking, refitting, dropping
  "bad" assets, widening a window until it works);
- the spec is ambiguous and a convenient interpretation happens to match the
  paper's headline result.

This skill complements Bench's
[robustness-auditor](../robustness-auditor/SKILL.md) (which audits a *finished*
run) by catching the same failure modes earlier, in the *code itself*.

## Reference Router

Load [references/backtest-pitfall-discipline.md](references/backtest-pitfall-discipline.md)
for the full distilled discipline: the leakage taxonomy, the multiple-testing
and selection-bias mechanics, the over-optimization funnel, and the expert-lens
checklist. Load it whenever a generation choice could affect measured
performance.

## The Pitfall Sweep

Run this sweep on the candidate before scoring it as acceptable.

### 1. Look-ahead and leakage

- Does any feature, rank, or fill use data dated after the decision time?
- Is every estimated quantity (means, vols, hedge ratios, scalers, model
  coefficients) fit on data `<= train_end` and frozen out-of-sample?
- Are labels/targets strictly future relative to features, with no overlap that
  bleeds the answer into the inputs?

### 2. Point-in-time and survivorship

- Is the eligible universe reconstructed *as of* each date, not filtered by
  who survived to the end of the sample?
- Are delisted/missing assets represented, not silently dropped?
- Are fields the ones available at decision time (no restated fundamentals)?

### 3. In-sample tuning

- Are parameters set from the spec or estimated in `fit(...)`, rather than
  chosen because they improved the score?
- No window/threshold was widened or nudged until the candidate passed.

### 4. Multiple testing and selection bias

- Across generation attempts, are **all** candidates and their scores recorded,
  not just the winner? Undisclosed trials are exactly how selection bias
  enters (the manifest records discarded trials for this reason).
- The number of attempts that produced the accepted candidate is visible, so a
  reviewer can deflate for it.

### 5. Overfitting the reproduction target

- The code implements the *method*; it does not encode a path to the paper's
  claimed metric (no hard-coded returns, no objective that rewards proximity to
  the claimed Sharpe).
- A held-out segment the generation loop never saw would still behave sanely.

### 6. Honest degradation

- The implementation does not assume frictionless fills, instant cancels, or
  full liquidity; where the spec implies costs/turnover, they are not silently
  removed to flatter the result.

## Decision Rule

If a shortcut makes the backtest look better without making the implementation
more faithful to the spec, **do not take it** — and if a convenient spec
interpretation happens to match the headline number, treat that as a warning,
not a confirmation. When a gap forces a guess that materially affects
performance, route it to [consult-reader](../consult-reader/SKILL.md) instead
of choosing the flattering option.

## Output Discipline

When asked to report rather than to edit code, return:

1. `pitfalls_found`: each issue, the stage it occurs in, and its likely effect
   on measured performance;
2. `leakage_check`: explicit pass/fail on look-ahead, point-in-time, and
   frozen-parameter discipline;
3. `trial_accounting`: how many candidates were tried and whether all were
   recorded;
4. `verdict`: emit / fix-first / consult-reader, with the single decisive
   reason.

## Guardrails

- A passing template test is not proof of validity; the no-lookahead test
  catches mechanical leakage, not conceptual overfitting.
- The holdout/walk-forward split does not by itself prevent overfitting if the
  loop iterates on out-of-sample feedback — every iteration spends OOS
  information.
- Never improve a score by hiding trials, dropping assets, or peeking.
- Do not issue investment advice.
