# Avellaneda-Stoikov Limit-Order-Book Market Making

Source: Marco Avellaneda and Sasha Stoikov, *High-frequency trading in a
limit order book*.

## Why This Source Matters

This paper is the canonical inventory-aware market-making model. It gives a
clean decomposition between an inventory-adjusted reservation price and an
optimal quoted spread. Use it to understand a paper's control logic, then use
its omissions as a checklist for whether the proposed strategy can survive an
actual matching engine.

## Core Model

- The midprice follows an arithmetic Brownian motion with constant volatility,
  no drift, and no serial dependence.
- Buy and sell market-order arrivals are independent Poisson processes.
- Fill intensity decreases with quote distance from the midprice, commonly
  simplified to `lambda(delta) = A exp(-k delta)`.
- The dealer maximizes exponential utility of terminal wealth.
- Quotes can be updated continuously and without cancellation cost.

The solution first computes a reservation price, shifted below the mid when
inventory is long and above it when inventory is short. It then places a
spread around that reservation price. Risk aversion, volatility, horizon, and
inventory determine the reservation-price shift; order-arrival sensitivity
helps determine the spread.

## What The Model Teaches

- Inventory risk should alter quote placement before inventory limits bind.
- A quote's economic value depends on its fill probability, not only its edge
  to mid.
- Risk aversion can reduce P&L variance and terminal inventory while also
  reducing average P&L.
- Market making is a joint pricing and stochastic-control problem.

## Assumptions To Challenge

The model focuses on inventory risk, not a rich model of adverse selection.
It omits:

- queue position and price-time priority;
- discrete ticks and minimum spread;
- latency, stale quotes, and cancel/replace races;
- fees, maker rebates, and exchange throttles;
- partial fills and order-size choice;
- hidden liquidity and competing venues;
- self-impact and strategic reactions by other traders.

The spread's independence from inventory in the approximation is partly a
consequence of the exponential-arrival specification. Do not treat that as a
universal market-making result.

## Simulation Diagnostics

The paper compares the inventory strategy with symmetric quoting around the
midprice in its own simulator. Treat this as a mechanism demonstration, not
venue-valid evidence.

Ask:

- How is `A` and `k` estimated, and does the estimate condition on queue
  position, state, side, and regime?
- Does the event clock permit multiple arrivals between decisions?
- Are quotes unrealistically canceled before adverse fills arrive?
- Does the benchmark face identical latency, fees, and fill logic?
- Are results robust when arrivals are clustered, mutually dependent, or
  informative?

The paper itself notes that simulation time-step choice is subtle: too small a
step lets the strategy update constantly without seeing orders; too large a
step compresses multiple events.

## Reviewer Use

Use this source when a paper claims an Avellaneda-Stoikov-style strategy.
Require the authors to distinguish:

1. the elegant control problem;
2. the calibrated fill model;
3. the venue-specific execution implementation;
4. the empirical evidence that survives realistic fills.

The most important falsification is to replace distance-only Poisson fills
with a queue-, latency-, and toxicity-aware execution model.

## Source Map

- Model setup: midprice, cash, inventory, and Poisson fills
- Utility formulation and Hamilton-Jacobi-Bellman equation
- Reservation price and approximate optimal quotes
- Numerical simulations and inventory-strategy comparison

