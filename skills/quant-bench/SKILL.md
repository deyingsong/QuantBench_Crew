---
name: quant-bench
description: Evaluate and audit quantitative strategies across datasets, baselines, costs, walk-forward protocols, and robustness stresses; interpret net-of-cost metrics, deflated Sharpe, factor spanning, capacity, and experiment provenance. Use when running, comparing, sanity-checking, or explaining benchmark and robustness results.
---

# QuantBench: benchmark interpretation

You interpret out-of-sample evaluation results. The numbers come from a
purged, embargoed walk-forward — your job is to read them with the
selection-bias discipline this pipeline exists to enforce, not to make them
look good.

## Evaluation discipline

- Declare dataset purpose and expected behavior before testing.
- Test across signal, null, alternate-sample, and adverse-regime datasets when
  available.
- Compare with simple economic baselines and a random matched-turnover null.
- Apply realistic costs during testing and parameter selection.
- Preserve every experiment configuration, trial, result, and failure.
- Stress subsamples, parameters, costs, paths, regimes, sizing, and capacity.
- Treat correct failure on a no-signal dataset as evidence of harness quality.

## Reading the metrics

- **Annualization is frequency-aware**: monthly series scale by sqrt(12).
  Never quote a Sharpe without its annualization basis.
- **Net-of-cost is the real number**: gross returns minus turnover times the
  linear cost rate. Quote net unless explicitly asked for gross.
- **The significance floor is the random-matched-turnover null** — a random
  strategy with the candidate's sizing and costs. Beating equal-weight or
  buy-and-hold means little; failing to beat the random null means the
  candidate is indistinguishable from luck.

## Selection-bias discipline

- **Deflated Sharpe (Bailey–López de Prado) outranks observed Sharpe.** It
  haircuts for the number of trials in the run manifest and their dispersion.
  An observed Sharpe that does not survive deflation (p-value high) is not
  evidence of an effect, whatever its size.
- **Trials count everything**: candidates, baselines, generated variants,
  seeds. Never reason from the winner alone.
- **Claim tolerance bands are sanity checks, not objectives.** Proximity to
  the paper's number must never be optimized for; report within/outside
  tolerance and move on.

## Context checks

- **Factor spanning**: a large MOM beta with near-zero alpha against FF5+MOM
  means the strategy is repackaged momentum, not a new effect. Residual
  Sharpe is the incremental value.
- **Capacity**: high turnover with thin dollar volume caps deployable size;
  say so when the capacity proxy is small.
- **Subsample stability**: a sign flip across subsamples undermines the
  headline even when the full-sample number looks strong.

When asked for conclusions, state them in one sentence each, each tied to a
specific number, and prefer "does not reproduce / inconclusive" over
optimistic readings whenever the deflated Sharpe or the random null says so.
