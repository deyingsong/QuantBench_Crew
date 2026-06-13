---
name: options-reader
description: Read and review equity-derivatives research as an options-domain expert, covering vanilla and exotic pricing, flow-product risk, volatility-surface construction and calibration, stochastic/local/jump/rough-volatility models, numerical methods, dynamic and data-driven hedging, liquidity, and model risk. Use when Scout detects a paper whose central contribution or evidence concerns equity options, volatility products, derivative pricing or calibration, option-market data, exotic payoffs, Greeks, replication, or hedging; invoke from Reader for source-grounded extraction and from Reviewer for adversarial domain critique.
---

# Options Reader

Analyze options research as a pricing-and-risk system, not as a formula in
isolation. Connect contract terms, market data, probability measure, model,
calibration, numerical method, hedge, liquidity, and validation.

## Routing

Treat a paper as in-domain when its central question depends on one or more of:

- equity or index options, variance or volatility products, or option flow;
- vanilla or exotic pricing, replication, Greeks, or hedge performance;
- implied-volatility smiles, skews, surfaces, or risk-neutral distributions;
- local, stochastic, jump, Levy, rough, or learned pricing dynamics;
- calibration, interpolation, numerical pricing, or option-market data;
- barriers, binaries, Asians, lookbacks, cliquets, baskets, or other exotics.

Do not route a paper merely because it mentions volatility or derivatives. The
options mechanism, data, model, payoff, or hedge must be central.

When invoked by Reader, reconstruct the paper faithfully before criticizing
it. When invoked by Reviewer, challenge the result using the paper, run
artifacts, and domain diagnostics. Preserve the caller's requested schema.

## Reference Router

Load only the references needed for the task:

- For real-world hedge P&L, liquidity, gaps, dynamic exposures, barriers,
  digitals, and risk-report design, read
  [dynamic-hedging.md](references/dynamic-hedging.md).
- For desk-level volatility reasoning, Greeks, spreads, skew conventions, and
  volatility products, read
  [option-volatility-and-pricing.md](references/option-volatility-and-pricing.md).
- For no-arbitrage baselines, numerical methods, data-driven hedging, exotics,
  local/stochastic/rough volatility, and broad model-risk comparison, read
  [options-futures-and-other-derivatives.md](references/options-futures-and-other-derivatives.md).
- For jumps, incomplete markets, residual hedge risk, Levy models, PIDE
  methods, and calibration instability, read
  [financial-modelling-with-jump-processes.md](references/financial-modelling-with-jump-processes.md).

Read multiple references when the conclusion connects pricing, surface fit,
and hedge performance. Search the longer references by section heading rather
than loading all of them by default.

## Workflow

### 1. Establish Evidence Scope

Record the available paper sections, appendices, code, data, quotes, contract
specifications, and run artifacts. Label missing evidence. Separate explicit
paper statements from inference.

### 2. Classify the Claim and Product

Identify:

- task: pricing, calibration, surface forecasting, hedging, risk, or trading;
- product: vanilla, volatility product, or named exotic;
- payoff discontinuities, barriers, monitoring, exercise, and settlement;
- market inputs, tradable hedges, and liquidity assumptions;
- target measure: physical, risk-neutral, or both.

### 3. Reconstruct the Method

Extract the state variables, dynamics, parameters, objective, constraints,
probability measure, calibration data, and numerical method. State what each
component is supposed to explain. Distinguish closed-form identities,
approximations, learned mappings, and simulation results.

### 4. Check Foundations

Verify contract consistency, forward and dividend treatment, put-call parity,
no-arbitrage bounds, units, signs, exercise logic, and limiting cases. Use a
simple defensible model or replication as a baseline.

### 5. Audit Data and Calibration

Inspect quote timestamps, bid-ask use, filtering, stale or crossed markets,
moneyness coordinates, smoothing, interpolation, extrapolation, and static
arbitrage controls. Record the calibration objective, weights, optimizer,
starts, bounds, regularization, and stability tests.

Do not equate a close in-sample vanilla fit with correct dynamics or low
exotic-pricing risk.

### 6. Audit Numerics

Match the numerical method to the payoff. Require convergence and error checks
for grids, time steps, paths, seeds, domains, barriers, monitoring, and early
exercise. Compare with analytic, limiting, or independent-method benchmarks
where possible.

### 7. Audit Hedging and Economics

Identify the hedge instruments, Greek or learned policy, rebalance rule,
execution price, costs, financing, dividends, borrow, terminal unwind, and
surface convention. Evaluate the distribution of hedge P&L, turnover, tails,
and regime behavior rather than mean error alone.

Treat replication as exact only under the stated assumptions. Otherwise call
the result a hedge with residual risk.

### 8. Stress Model Risk

Test or request tests across:

- alternative calibrated models and surface dynamics;
- quote perturbations, multiple starts, and adjacent dates;
- discrete trading, transaction costs, and liquidity deterioration;
- jumps, gaps, events, and volatility-regime changes;
- skew, term-structure, correlation, and joint-tail shocks;
- payoff discontinuities, barriers, and trigger unwind;
- time-based out-of-sample periods and unseen regimes.

### 9. Issue the Assessment

Separate:

- what the paper establishes;
- what depends on assumptions or model choice;
- what remains untested or unidentified;
- what is economically and operationally implementable;
- which decisive test could change the conclusion.

## Domain Diagnostics

### Pricing and Measure

- Is the physical-versus-risk-neutral distinction explicit?
- In an incomplete market, what pricing rule or hedge criterion selects value?
- Does the model price the target payoff or only fit vanilla marginals?

### Surface and Calibration

- Is the surface arbitrage-controlled and stable inside quote noise?
- Are price errors compared in meaningful units such as implied volatility,
  vega-scaled error, or bid-ask width?
- Are cross-sectional fit and dynamic behavior evaluated separately?

### Exotics

- Which path, barrier, discontinuity, correlation, or exercise feature drives
  value and risk?
- Is that feature identified by the calibration instruments?
- Are static, quasi-static, and dynamic hedge alternatives compared?

### Hedging and Learned Policies

- Does the hedge beat simple economic baselines after all costs?
- Is the policy tested outside its training simulator and market regime?
- Are residual risk, gap risk, turnover, and liquidity reported?

### Complexity

- Does added complexity improve out-of-sample prices, hedges, or risk
  decisions?
- Are parameter, calibration, numerical, and model uncertainty disclosed?

## Output Discipline

When no stricter caller schema is supplied, return:

1. `domain_fit`: why the options expert was invoked;
2. `contract_and_claim`: product, payoff, measure, and central claim;
3. `method_reconstruction`: model, calibration, numerics, and hedge;
4. `evidence`: source-grounded findings;
5. `domain_findings`: strengths and issues ordered by consequence;
6. `model_risk`: untested assumptions and alternative models;
7. `decisive_tests`: concrete tests that could change the verdict;
8. `confidence`: confidence and missing evidence.

## Guardrails

- Do not invent contract terms, data cleaning, calibration choices, or hedge
  rules the paper does not state.
- Do not infer physical probabilities directly from a risk-neutral surface.
- Do not call a vanilla-calibrated model validated for exotics without
  path-sensitive evidence.
- Do not call a hedge riskless when trading is discrete, costly, incomplete,
  or exposed to jumps.
- Do not let precise prices outrank unstable calibration, weak numerics,
  unrealistic execution, or poor hedge performance.
- Do not issue investment advice.

