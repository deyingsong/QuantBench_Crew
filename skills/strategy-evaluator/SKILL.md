---
name: strategy-evaluator
description: Evaluate a quantitative strategy across declared datasets, realistic costs, baseline models, and portfolio-relevant performance metrics. Use when Bench must compare a candidate with nulls or simple alternatives, test expected behavior in signal and no-signal worlds, or decide whether an apparent edge survives outside one backtest.
---

# Strategy Evaluator

Evaluate a research process, not its prettiest equity curve. A strategy earns
attention only when it behaves as expected across declared datasets and beats
appropriate baselines after realistic costs.

## Workflow

1. Read `references/evaluation-discipline.md`.
2. Declare every dataset and its expected behavior before running experiments.
3. Record dataset version, content hash, sample, frequency, and configuration.
4. Use purged, embargoed walk-forward evaluation when model fitting or
   parameter selection is involved.
5. Apply costs during optimization and evaluation, never as an afterthought.
6. Compare with simple economic baselines and a random matched-turnover null.
7. Report frequency-aware return, risk, drawdown, tail, turnover, capacity,
   and portfolio-contribution metrics.
8. Evaluate signal worlds and no-signal worlds. A strategy should find the
   planted effect and reject noise.
9. Count all trials and preserve every result, including failures.
10. State whether each dataset behaved as expected and whether the strategy
    passed the declared evaluation suite.

## Output Contract

Return experiments with:

- dataset provenance and declared `expect_edge`;
- complete evaluation configuration;
- candidate metrics and baseline metrics;
- random-null verdict and expectation verdict;
- claim comparisons, statistical corrections, and notes;
- cross-dataset pass rate and an overall conclusion.

## Guardrails

- Never optimize toward a paper's headline number.
- Never compare gross candidate returns with net baseline returns.
- A complex strategy must beat simple alternatives on the same information.
- High Sharpe does not override drawdown, tail risk, capacity, or trial count.
- Do not interpret failure on a deliberately no-signal dataset as a weakness;
  correctly rejecting noise is evidence of evaluation integrity.
