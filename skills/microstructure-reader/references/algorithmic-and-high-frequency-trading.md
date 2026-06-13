# Cartea-Jaimungal-Penalva Algorithmic And High-Frequency Trading

Source: Alvaro Cartea, Sebastian Jaimungal, and Jose Penalva, *Algorithmic and
High-Frequency Trading*.

## Why This Source Matters

This book unifies electronic-market mechanics, market impact, optimal
execution, limit-order placement, market making, adverse selection, and
order-flow signals through stochastic control. Use it to inspect whether a
strategy's objective, state variables, and impact assumptions correspond to
the actual trading problem.

## Market-Mechanics Foundation

The book distinguishes market and limit orders, describes LOB events, and
connects spread, depth, resilience, volatility, and price impact to market
quality. It also warns against equating liquidity provision with uninformed
trading or liquidity taking with informed trading.

For empirical work, identify:

- what messages are observed;
- how the LOB is reconstructed;
- how market-order direction is assigned;
- whether displayed depth represents executable depth;
- how venue fees and order types enter the decision.

## Impact And Execution

Optimal liquidation balances urgency and risk against transaction costs.
Models commonly separate:

- temporary impact, associated with immediate execution and walking the book;
- permanent impact, associated with lasting price changes;
- spread and other explicit costs;
- risk from delaying execution.

The book illustrates linear impact models and shows that estimated impact
varies materially within the day. Treat a constant impact parameter as a
conditional approximation.

Review:

- how temporary and permanent impact are identified;
- whether other traders' order flow is controlled for;
- whether impact is causal or merely correlated with information;
- whether the agent's size is small relative to market volume;
- whether the strategy permits unrealistic instantaneous trading or free
  reversal;
- whether lit and dark fills are modeled with realistic selection.

## Market Making And Adverse Selection

The market-making chapters incorporate inventory aversion, order arrivals,
short-term alpha, and adverse selection. A useful decomposition is:

- value from spread capture;
- inventory-risk cost;
- loss from fills before unfavorable price moves;
- value from predictive order-flow signals.

Require post-fill markouts over multiple horizons. A high fill rate can be a
sign of stale or toxic quotes rather than success.

## Control-Model Diagnostics

For every stochastic-control result, state:

- objective function and terminal penalty;
- state variables and controls;
- admissibility constraints;
- dynamics assumed for price, order flow, and fills;
- impact functions;
- boundary and terminal conditions;
- calibration method.

Then test whether omitted state variables, such as queue position, latency,
spread state, or venue, are material enough to invalidate the policy.

## Generalization

Several empirical illustrations use particular NASDAQ stocks and historical
periods. Do not transport calibrated impact or order-flow relationships to
other instruments, dates, or venues without re-estimation. Validate across
liquidity, volatility, spread, and order-flow regimes.

## Source Map

- Parts I-II: electronic markets, LOBs, market quality, and control methods
- Chapters 6-9: optimal execution and limit-order strategies
- Chapter 10: market making and adverse selection
- Later chapters: order-flow and statistical trading strategies

