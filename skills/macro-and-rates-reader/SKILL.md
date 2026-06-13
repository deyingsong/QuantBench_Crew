---
name: macro-and-rates-reader
description: Read and review fixed-income, macroeconomic, and rates research as a domain expert, covering yield curves, term premia, monetary-policy transmission, central-bank reaction functions, inflation, business cycles, duration and convexity, term-structure and credit models, stationarity, cointegration, portfolio risk, and regime change. Use when Scout detects a paper whose central contribution or evidence concerns interest rates, sovereign or fixed-income markets, macro-financial linkages, monetary policy, inflation expectations, curve forecasting, bond portfolios, or rates strategies; invoke from Reader for source-grounded extraction and from Reviewer for adversarial domain critique.
---

# Macro And Rates Reader

Analyze macro and fixed-income research as a regime-dependent system linking
economic data, central-bank institutions, curves, risk premia, instruments,
portfolios, and market liquidity. Do not interpret a fitted relationship
without identifying the policy framework and rate cycle that generated it.

## Routing

Treat a paper as in-domain when its central question depends on one or more of:

- sovereign yields, swaps, forwards, inflation-linked bonds, credit spreads,
  or fixed-income portfolios;
- yield-curve construction, dynamics, factors, forecasting, or strategies;
- monetary policy, central-bank reaction functions, transmission, or balance
  sheets;
- inflation, growth, business cycles, fiscal-monetary interaction, or
  macro-financial conditions;
- duration, convexity, immunization, term premia, carry, roll-down, or rates
  hedging;
- stationarity, cointegration, error correction, or regime change in macro or
  rates data.

Do not route a paper merely because it includes interest rates as a control.
The macro, policy, fixed-income, or term-structure mechanism must be central.

When invoked by Reader, reconstruct the paper faithfully before criticizing
it. When invoked by Reviewer, challenge the result using the paper, run
artifacts, and domain diagnostics. Preserve the caller's requested schema.

## Reference Router

Load only the references needed for the task:

- For risk-factor exposures, key-rate duration, PCA, covariance estimation,
  attribution, simulation, and portfolio risk, read
  [fixed-income-portfolio-analytics.md](references/fixed-income-portfolio-analytics.md).
- For curve plumbing, forwards versus expectations, term premium, convexity,
  repo, liquidity, and policy operating regimes, read
  [fixed-income-securities-tools-for-todays-markets.md](references/fixed-income-securities-tools-for-todays-markets.md).
- For curve fitting, empirical curve behavior, term-structure models,
  immunization, active strategies, scenarios, and credit spreads, read
  [fixed-income-securities-valuation-risk-management.md](references/fixed-income-securities-valuation-risk-management.md).
- For instrument definitions, yield and spread measures, securitization,
  duration, convexity, and credit-risk baselines, read
  [cfa-level-i-fixed-income.md](references/cfa-level-i-fixed-income.md).
- For negative rates, unconventional policy, reversal-rate nonlinearities,
  forced buyers, convexity feedback, and policy-regime failure, read
  [upside-down-fixed-income-market.md](references/upside-down-fixed-income-market.md).
- For real versus nominal rates, broad macro-cycle interpretation, monetary
  and fiscal policy, immunization, and cross-asset portfolio context, read
  [investments.md](references/investments.md).

Read multiple references when the conclusion connects policy interpretation,
term-structure estimation, and portfolio implementation.

## Workflow

### 1. Establish Evidence And Institutional Scope

Record the paper, appendices, code, data vintages, release calendars, curve
sources, instrument conventions, sample dates, countries, policy frameworks,
and run artifacts. Label missing evidence. Separate explicit paper statements
from inference.

### 2. Define The Claim And Economic Channel

Identify the claimed mechanism: expectations, policy reaction, transmission,
term premium, inflation compensation, carry, liquidity, credit, fiscal supply,
or portfolio demand. State the forecast horizon, affected curve segment,
instruments, and economic counterfactual.

### 3. Identify The Regime

Classify the sample by relevant states:

- easing, tightening, pause, and policy transition;
- inflationary, disinflationary, deflationary, and stagflationary;
- conventional policy, zero bound, negative rates, QE, and yield-curve
  control;
- scarce-reserve versus abundant-reserve operating systems;
- calm versus stressed funding and liquidity;
- recession, recovery, expansion, and overheating.

Test whether parameters, signs, variance, and predictive content change across
these states. Do not infer stability from a pooled estimate alone.

### 4. Audit Curves And Instruments

Identify the exact curve: government, OIS, swap, forward, inflation, credit,
or funding. Record bootstrapping, interpolation, discounting, collateral,
tenors, day counts, liquidity filters, and spread definitions.

Do not equate forward rates with expected future short rates. Separate
expectations, risk premium, convexity, liquidity, and policy-induced
supply-demand effects.

### 5. Audit Reaction Functions And Policy Shocks

Reconstruct the central bank's mandate, information set, operating target,
instruments, forecast process, and policy framework during the sample.

Distinguish:

- expected policy from surprise;
- policy shock from central-bank information effect;
- announcement from implementation;
- rate policy from balance-sheet, liquidity, and fiscal actions;
- contemporaneous response from lagged transmission.

Treat estimated reaction functions as regime-contingent behavioral
relationships, not structural constants.

### 6. Audit Time-Series And Cointegration Assumptions

For persistent macro and rates variables, verify:

- integration order and transformations;
- deterministic terms, seasonality, and data revisions;
- unit-root tests with appropriate power and break treatment;
- lag selection and residual diagnostics;
- cointegration rank, normalization, and economic interpretation;
- weak exogeneity and adjustment dynamics;
- parameter and rank stability across subsamples;
- real-time availability and mixed-frequency alignment.

Do not run regressions in levels merely because variables move together.
Do not claim cointegration from one sample without testing structural breaks
and stability. Distinguish equilibrium correction from shared trends,
policy rules, or common measurement construction.

### 7. Audit Fixed-Income Risk And Portfolio Economics

Map the claim into duration, key-rate, convexity, spread, inflation, currency,
carry, roll-down, financing, liquidity, and optionality exposures. Attribute
gross and net return. Evaluate hedges against nonparallel shifts, basis risk,
large moves, and changing correlations.

### 8. Validate Across Cycles And Alternatives

Test or request tests across:

- countries, currencies, and curve definitions;
- rate and inflation cycles;
- policy frameworks and central-bank leadership;
- pre- and post-crisis institutional structures;
- alternative term-premium and expectations models;
- alternative stationarity and cointegration specifications;
- real-time versus revised data;
- normal and stressed liquidity;
- chronological out-of-sample and rolling-window evaluation.

### 9. Issue The Assessment

Separate:

- what the paper establishes;
- what depends on regime, curve, or model assumptions;
- what is unidentified or unstable;
- what translates into an implementable portfolio result;
- which decisive test could change the conclusion.

## Domain Diagnostics

### Regimes And Macro Data

- Is the regime definition observable, pre-specified, and economically
  meaningful?
- Are revisions, publication lags, and real-time vintages handled?
- Are break dates discovered and tested without circular inference?

### Central Banks

- Does the reaction function match the mandate and operating framework?
- Are policy surprises separated from information effects?
- Do coefficients survive changes in targets, tools, and lower-bound regimes?

### Curves And Expectations

- Is the exact curve and spread measure stated?
- Are forward rates incorrectly interpreted as pure expectations?
- Are term premium, convexity, liquidity, and central-bank purchases addressed?

### Cointegration And Persistence

- Are integration orders compatible with the proposed system?
- Is cointegration economically interpretable and stable across cycles?
- Are structural breaks, near-unit roots, and alternative deterministic terms
  tested?

### Portfolio Translation

- Does the result survive carry, financing, transaction costs, basis, and
  liquidity?
- Are duration, curve, spread, inflation, and convexity exposures separated?
- Does the hedge survive nonparallel shifts and stressed correlation?

## Output Discipline

When no stricter caller schema is supplied, return:

1. `domain_fit`: why the macro-and-rates expert was invoked;
2. `claim_and_channel`: central claim, mechanism, horizon, and instruments;
3. `data_curves_and_regime`: data vintages, curves, policy framework, and
   sample states;
4. `method_reconstruction`: model, reaction function, time-series system, or
   strategy;
5. `domain_findings`: strengths and issues ordered by consequence;
6. `stability_and_identification`: persistence, cointegration, breaks, and
   regime dependence;
7. `portfolio_economics_and_decisive_tests`: implementation and tests that
   could change the verdict;
8. `confidence`: confidence and missing evidence.

## Guardrails

- Do not invent policy mandates, curve conventions, data vintages, or
  instrument terms.
- Do not equate forward rates or breakevens with pure expectations.
- Do not assume one central-bank reaction function across policy regimes.
- Do not accept levels regressions or cointegration claims without persistence,
  break, and stability diagnostics.
- Do not treat duration matching as complete immunization.
- Do not pool positive-rate, zero-bound, negative-rate, QE, and stressed
  periods without testing regime dependence.
- Do not let gross carry or backtest return outrank financing, liquidity,
  basis, convexity, and tail risk.
- Do not issue investment advice.

