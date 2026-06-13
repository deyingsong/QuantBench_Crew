# Institutional Review Checklist

## Claim Integrity

- Are headline claims falsifiable and sourced?
- Were all material claims tested?
- Are claimed and achieved values definitionally comparable?
- Are negative and null findings preserved?

## Data Integrity

- Are dataset versions, timestamps, and transformations recorded?
- Are survivorship, delisting, revisions, and look-ahead controlled?
- Is proprietary data described sufficiently to understand the dependency?
- Can a third party obtain or replace the data?

## Method Integrity

- Are equations, algorithms, hyperparameters, and tie-breaking rules specified?
- Are preprocessing and feature availability aligned with prediction time?
- Is model selection separated from final evaluation?
- Are code and environment artifacts auditable?

## Evaluation Integrity

- Are simple, incumbent, and random baselines included?
- Is the test genuinely out of sample?
- Are trial counts and failed variants disclosed?
- Are multiple testing and selection bias addressed?
- Are costs, financing, slippage, turnover, and capacity realistic?

## Robustness

- Does the sign persist across subsamples and regimes?
- Does performance survive seeds and parameter perturbations?
- Does it reject no-signal datasets?
- Does it survive conservative cost and liquidity stress?
- Are failed and unavailable checks visible?

## Economic And Portfolio Value

- Why should the edge exist and persist?
- Who is on the other side?
- Is the result a repackaged known factor?
- Does it improve a portfolio after covariance, costs, and constraints?
- Is a simpler low-cost approach preferable?

## Risk And Survival

- What are drawdown, leverage, liquidity, concentration, and tail risks?
- What happens under adverse regimes?
- How sensitive is sizing to estimation error?
- Could the strategy or organization survive the plausible worst case?

## Incentives And Governance

- Who benefits from a favorable result?
- Are experiment, model, and data owners accountable?
- Are conflicts, access, and overrides controlled?
- Can an independent reviewer reproduce the decision trail?
- Are model limitations monitored after deployment?

## Decision Gate

A `promising` verdict requires more than a good backtest. At minimum:

- meaningful claims reproduce
- the strategy beats appropriate baselines and random nulls
- results survive multiple-testing correction and robustness checks
- implementation and data provenance are credible
- no critical validity or governance issue remains

Missing critical evidence should keep the verdict conservative.
