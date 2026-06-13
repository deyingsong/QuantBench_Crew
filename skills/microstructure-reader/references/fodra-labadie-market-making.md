# Fodra-Labadie Inventory-Constrained Market Making

Source: Pietro Fodra and Mauricio Labadie, *High-frequency market-making with
inventory constraints and directional bets*.

## Why This Source Matters

This paper extends inventory-aware market making to non-martingale midprices,
general utility, directional views, and an explicit terminal inventory
penalty. It is useful for separating alpha-taking from inventory control and
for asking whether a market-making paper quietly earns its returns from a
directional forecast.

## Core Model

- Limit-order executions arrive through independent Poisson processes with
  intensity decreasing exponentially with quote distance.
- The midprice may have drift or mean reversion, rather than being restricted
  to a martingale.
- The market maker maximizes expected utility with a terminal quadratic
  inventory penalty controlled by `eta`.
- Directional expectations shift the indifference price and create asymmetric
  quotes.
- The proposed formulas use first-order approximations to the control problem.

In the examples, arithmetic Brownian and Ornstein-Uhlenbeck dynamics illustrate
how expected future price changes can be embedded into quote placement.

## What The Model Teaches

- A directional view and inventory aversion can move quotes in similar ways;
  reviewers must identify which mechanism drives results.
- The terminal inventory penalty directly controls end inventory and
  indirectly changes P&L.
- Utility risk aversion directly changes the P&L distribution and indirectly
  changes inventory.
- Mean-reversion forecasts can improve average P&L while worsening inventory
  and tail risk.

## Explicit Limitations

The paper is unusually helpful about its simplifications:

- only limit orders are modeled;
- terminal inventory is liquidated at the midprice;
- the external market spread is effectively zero;
- impact is represented only through the maker's half-spread;
- the prevailing spread should really be another state variable;
- one- or two-tick markets create problems because a minimum price move can
  cross a quote;
- the first-order policy is an approximation, not a proof of global optimality.

Although adverse selection motivates market making, the execution model does
not richly represent informed order flow, queue depletion, latency, or toxic
fills.

## Reviewer Diagnostics

When directional bets improve a market-making strategy, ask:

- Does the same forecast work after removing spread capture?
- Is the forecast measurable before quote placement?
- Does improved mean P&L come with larger inventory or left-tail exposure?
- Is terminal inventory charged an executable liquidation cost?
- Does the result survive a nonzero, time-varying spread and discrete ticks?
- Are arrival intensities stable across trend, mean-reversion, and stress
  regimes?

Require separate attribution for:

- passive spread capture;
- inventory revaluation;
- directional alpha;
- fees and rebates;
- terminal liquidation;
- adverse-selection losses after fills.

## Reviewer Use

Use this source for papers that add alpha signals to market making. Its main
lesson is not that a directional market maker is superior, but that objective
functions and terminal penalties can hide materially different risk-taking.
Compare strategies at matched inventory risk and executable liquidation cost.

## Source Map

- Stochastic-control setup and general midprice dynamics
- Indifference prices and optimal spread approximations
- Directional bets under arithmetic Brownian and mean-reverting prices
- Simulation comparisons and sensitivity to `eta` and risk aversion
- Conclusion and stated model limitations

