---
name: factor-reader
description: Read and review cross-sectional equity factor, anomaly, characteristic, and smart-beta research as a domain expert, covering portfolio sorts, independent double sorts, Fama-MacBeth regressions, factor-model alpha, multiple testing, point-in-time data, post-publication decay, portfolio construction, costs, capacity, and regime robustness. Use when Scout detects a paper whose central contribution or evidence concerns the cross-section of expected equity returns, stock characteristics, factor premiums, anomaly discovery, characteristic-managed portfolios, or equity factor timing; invoke from Reader for source-grounded extraction and from Reviewer for adversarial domain critique.
---

# Factor Reader

Analyze equity-factor research as a claim about information available at
portfolio formation, cross-sectional expected returns, benchmark
distinctiveness, and implementable net performance. Do not accept a
significant long-short spread without reconstructing the research search,
universe, controls, factor models, and post-discovery evidence.

## Routing

Treat a paper as in-domain when its central question depends on one or more of:

- stock characteristics, anomalies, factor premiums, or smart beta;
- cross-sectional return prediction or characteristic-managed portfolios;
- portfolio sorts, double sorts, or Fama-MacBeth regressions;
- factor construction, spanning, redundancy, or factor-model alpha;
- equity factor timing, combination, crowding, or post-publication decay;
- implementation of long-short or long-only equity factor portfolios.

Do not route a paper merely because it uses factors as controls or trades an
equity strategy. The cross-sectional equity characteristic, factor premium,
or factor-model contribution must be central.

When invoked by Reader, reconstruct the paper faithfully before criticizing
it. When invoked by Reviewer, challenge the result using the paper, run
artifacts, and domain diagnostics. Preserve the caller's requested schema.

## Reference Router

Load only the references needed for the task:

- For characteristic construction, cross-sectional factor returns, alpha
  versus hidden exposure, factor neutrality, risk attribution, sizing, and
  optimization, read
  [advanced-portfolio-management.md](references/advanced-portfolio-management.md).
- For signal-to-noise, breadth, multiple testing, out-of-sample validation,
  information decay, smart beta versus pure alpha, costs, and capacity, read
  [advances-in-active-portfolio-management.md](references/advances-in-active-portfolio-management.md).
- For implementation shortfall, market impact, timing risk, opportunity cost,
  cost-risk trade-offs, and post-trade analysis, read
  [optimal-trading-strategies.md](references/optimal-trading-strategies.md).
- For point-in-time defactorization, residual-return models, new risk factors,
  crowding, and structural change, read
  [statistical-arbitrage.md](references/statistical-arbitrage.md).
- For ranking portfolios, backtest biases, true out-of-sample tests,
  shortability, timing, costs, and regime shifts, read
  [algorithmic-trading-winning-strategies.md](references/algorithmic-trading-winning-strategies.md).
- For target-to-order translation, DMA feasibility, order handling, and
  operational execution controls, read
  [algorithmic-trading-and-dma.md](references/algorithmic-trading-and-dma.md).

Read multiple references when a conclusion connects statistical discovery,
factor-model distinctiveness, portfolio construction, and implementation.

## Workflow

### 1. Establish Evidence And Research Timeline

Record the paper, appendices, code, data dictionary, data vendors, sample,
publication date, earlier working-paper dates, related practitioner use, and
run artifacts. Label missing evidence. Separate explicit paper statements
from inference.

Partition evidence into discovery, validation, post-publication, and genuinely
live or untouched periods. Record all disclosed signals and specifications
tried, not only the reported winner.

### 2. Define The Factor Claim And Mechanism

Identify the characteristic, expected-return claim, horizon, portfolio use,
and proposed mechanism: risk compensation, behavioral bias, institutional
friction, forced trading, information diffusion, liquidity provision, or
another channel.

Distinguish:

- a characteristic that predicts returns;
- a tradable factor portfolio;
- a systematic premium;
- alpha beyond existing factors;
- a timing rule for an existing factor.

Require testable implications of the proposed mechanism where possible.

### 3. Reconstruct Universe, Signal, And Timing

Document exchanges, security types, share codes, price and market-cap filters,
financial firms, microcaps, delistings, IPO seasoning, missing data, and the
shortable universe.

For every input, record its vintage, publication lag, revision policy, and
availability at portfolio formation. Audit accounting-data lags, constituent
history, corporate actions, delisting returns, and asynchronous timestamps.

Reconstruct the characteristic formula, transformations, winsorization,
standardization, neutralization, breakpoint source, rebalance frequency,
holding period, skip periods, and overlapping portfolios.

### 4. Audit Portfolio Sorts And Controls

For univariate sorts, verify the number of buckets, breakpoint universe,
weighting, rebalance date, holding period, and long-short definition. Report
the distribution of returns across all buckets, not only the extreme spread.

For double sorts, determine whether sorts are independent or dependent.
Independent sorts form breakpoints for both characteristics separately before
intersecting the portfolios; dependent sorts form candidate-characteristic
breakpoints within each control-characteristic group. Neither universally
dominates. Independent sorts preserve common breakpoints but may create sparse
cells when characteristics correlate. Dependent sorts improve within-control
comparability but make candidate breakpoints conditional on the control and
can conceal differences in the candidate's level across groups.

Challenge:

- NYSE versus full-universe breakpoints;
- equal-weight versus value-weight results;
- microcap and low-price concentration;
- coarse bins that leave residual confounding;
- too many bins that destroy power or create sparse cells;
- asymmetric or selectively reported controls;
- control variables chosen after seeing results.

No single double sort proves distinctiveness. Require a pre-specified set of
economically relevant controls and complementary regression evidence.

### 5. Audit Fama-MacBeth And Cross-Sectional Regressions

Reconstruct the period-by-period cross-sectional regression, dependent return
horizon, characteristics and controls, transformations, weighting, fixed
effects, and sample filters. Confirm regressors are known before the return
being predicted.

Evaluate:

- the time-series mean and stability of slope estimates;
- Newey-West or other HAC treatment for serial correlation, especially with
  overlapping returns;
- cross-sectional dependence and clustered or bootstrap alternatives;
- errors-in-variables and Shanken-type concerns when estimated betas enter;
- multicollinearity, correlated characteristics, and coefficient instability;
- economic magnitude, monotonicity, and incremental explanatory power;
- robustness to alternative scaling, winsorization, and specifications.

Do not accept a large average slope or `t > 2` without the trial count,
dependence structure, and economic effect.

### 6. Audit Factor-Model Alpha And Redundancy

Evaluate the candidate against economically appropriate benchmarks, typically
including CAPM, FF3, momentum where relevant, FF5, and HXZ/q-factor models,
plus contemporary alternatives justified by the paper's date and claim.

Match factor definitions, region, frequency, currency, weighting, and sample.
Distinguish alpha from loading and characteristic exposure. Test whether the
candidate:

- earns intercept alpha after established models;
- spans or is spanned by existing factors;
- adds to factor tangency or predictive portfolios;
- remains after characteristic controls and residual-return tests;
- merely repackages a known smart-beta exposure.

Failure to survive FF5 or HXZ is material evidence against *incremental
alpha*, but may still be consistent with a systematic premium already captured
by those models. State that distinction.

### 7. Audit Multiple Testing And Post-Publication Decay

Reconstruct the effective number of trials across characteristics,
transformations, horizons, universes, controls, and portfolio constructions.
Apply or request false-discovery, data-snooping, bootstrap, or deflated
performance corrections appropriate to the evidence.

Compare effect size and significance across:

- original discovery sample;
- internal holdout and international or cross-market replication;
- post-working-paper and post-journal-publication periods;
- periods before and after broad market adoption.

Do not automatically interpret post-publication decay as arbitrage. It may
reflect original overfitting, changing data construction, lower factor
premiums, crowding, costs, or regime shifts. Publication date may also be a
poor proxy for first dissemination.

### 8. Audit Portfolio Economics And Implementation

Map the result into factor, sector, beta, size, liquidity, volatility, and
short-side exposures. Attribute gross return and risk before calling the
effect stock-selection alpha.

Evaluate turnover, borrow, financing, short-sale constraints, spreads, market
impact, opportunity cost, capacity, crowding, and target-to-fill timing.
Require net performance under defensible cost models and stress assumptions.

Challenge results driven by equal-weight microcaps, impossible close prices,
unavailable shorts, concentrated rebalance dates, or portfolios too large
relative to liquidity.

### 9. Validate Generalization And Issue The Assessment

Test or request tests across subperiods, regions, sectors, market-cap and
liquidity buckets, bull and bear markets, high- and low-volatility states,
crises, structural changes, and alternative data definitions.

Separate:

- what the paper establishes;
- what is explained by known factors or controls;
- what may be a false discovery or sample artifact;
- what survives post-publication and implementation;
- which decisive test could change the conclusion.

## Domain Diagnostics

### Sort Design

- Are breakpoints, weights, and rebalances specified and point-in-time?
- Do independent double sorts and regression controls agree?
- Is the result monotonic or carried only by one extreme, microcap-heavy bin?

### Fama-MacBeth Inference

- Are regressors known before returns and consistently transformed?
- Do standard errors address overlapping returns and dependence?
- Are slope magnitudes stable, incremental, and economically meaningful?

### Factor Models

- Does alpha survive FF5, HXZ/q-factor, momentum, and justified contemporary
  alternatives?
- Is the candidate distinct from known factors in exposures and returns?
- Does the conclusion change with factor definitions or risk models?

### Discovery And Decay

- Is the full search space disclosed and multiple testing addressed?
- Does the signal survive untouched, international, and post-publication
  samples?
- Is decay consistent with arbitrage, crowding, structural change, or
  original overfit?

### Implementation

- Does net alpha survive costs, borrow, impact, delays, and capacity?
- Can the assumed portfolio be formed at the stated prices and timestamps?
- Are realized factor exposures consistent with the target portfolio?

## Output Discipline

When no stricter caller schema is supplied, return:

1. `domain_fit`: why the factor expert was invoked;
2. `factor_claim_and_mechanism`: characteristic, premium, horizon, and channel;
3. `data_universe_and_timing`: point-in-time inputs, filters, and sample;
4. `empirical_design`: sorts, Fama-MacBeth setup, inference, and trial count;
5. `benchmarks_and_distinctiveness`: controls, FF5/HXZ results, and redundancy;
6. `domain_findings`: strengths and issues ordered by consequence;
7. `decay_implementation_and_decisive_tests`: post-publication evidence, net
   economics, and tests that could change the verdict;
8. `confidence`: confidence and missing evidence.

## Guardrails

- Do not invent data lags, universe filters, attempted signals, or portfolio
  rules.
- Do not accept raw `t > 2` without accounting for multiple testing and
  dependence.
- Do not infer robustness from one univariate or double sort.
- Do not call a characteristic distinct alpha when it fails appropriate
  factor models or controls without explaining the interpretation.
- Do not use revised, current-constituent, or otherwise non-point-in-time data
  as if available historically.
- Do not call an equal-weight, microcap-driven spread scalable without
  implementation evidence.
- Do not confuse a systematic characteristic premium with idiosyncratic
  stock-selection alpha.
- Do not let gross returns outrank costs, borrow, capacity, crowding, and
  post-publication evidence.
- Do not issue investment advice.
