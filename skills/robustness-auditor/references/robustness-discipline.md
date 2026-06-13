# Transcript-Distilled Robustness And Audit Discipline

## What Robustness Means

A robust strategy is not merely profitable in one historical path. It retains
its economic meaning and acceptable risk under reasonable perturbations, while
failing honestly in worlds where its premise should not apply.

The corpus repeatedly warns that finance has low signal-to-noise, non-normal
returns, dependence, changing regimes, execution frictions, and severe
selection bias. Robustness work should therefore attack the strategy from
several independent directions.

## Required Checks

- **Research-trial audit:** count every candidate, parameter choice, seed,
  feature set, and reused holdout. Lopez de Prado's central warning is that
  selection bias plus backtest overfitting creates inflated winners.
- **Temporal stability:** use rolling/walk-forward tests and contiguous
  subsamples. Do not repair a failed holdout and continue calling it holdout.
- **Parameter stability:** prefer plateaus to isolated optima; small parameter
  changes should not destroy the result.
- **Cost stress:** apply commissions, slippage, spread, latency, market impact,
  and turnover costs during testing. Davey emphasizes that costs alter which
  parameters appear optimal, not merely final P&L.
- **Path stress:** use resampling, block bootstrap, or simulations to expose
  drawdown and path dependence. Preserve autocorrelation when relevant.
- **Scenario and regime stress:** test bull, bear, flat, volatile, illiquid,
  crisis, and generated future scenarios. Generated scenarios are models, not
  facts.
- **Universe/data stress:** vary markets, instruments, providers, periods, and
  sample filters while preserving point-in-time discipline.
- **Portfolio stress:** inspect correlations, factor spanning, concentration,
  capacity, leverage, and crowding.
- **Survival stress:** inspect drawdown distributions, expected shortfall,
  sizing, margin calls, and risk of ruin.

## Experiment Ledger

For every test record:

- unique experiment name and purpose;
- frozen strategy/version and code hash when available;
- dataset name, version, content hash, period, and seed;
- complete protocol and perturbation configuration;
- trial number and relation to prior tests;
- metrics and baseline results;
- pass/fail/unavailable verdict with acceptance rule;
- artifact and result hash.

Never delete failed experiments. A clean audit trail is part of the evidence.

## Interpretation

- One failed consequential stress can outweigh many cosmetic passes.
- Sign flips, isolated parameter peaks, cost sensitivity, and noise-world
  success are strong fragility signals.
- A high observed Sharpe with weak deflated Sharpe is not robust.
- Diversification can reduce portfolio risk, but correlated strategies may
  fail together in crises.
- Conservative sizing improves survival; full Kelly or excess leverage can
  turn a genuine edge into ruin.
- Live and incubation performance are the ultimate external tests, but they
  do not excuse weak research controls.

## Provenance

Distilled from all requested folders, with particular weight on Lopez de
Prado's backtest-overfitting material; Ernest Chan's statistical-significance
and backtesting-pitfall material; Kevin Davey's walk-forward, Monte Carlo,
cost, and risk-of-ruin workflows; QuantInsti scenario/regime testing; and the
portfolio/risk lenses of Thorp, Markowitz, Sharpe, Asness, and Dalio.
