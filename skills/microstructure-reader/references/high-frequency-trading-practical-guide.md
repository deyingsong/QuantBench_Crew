# Aldridge High-Frequency Trading Practical Guide

Source: Irene Aldridge, *High-Frequency Trading: A Practical Guide to
Algorithmic Strategies and Trading Systems*.

## Why This Source Matters

This source provides a broad practical map from tick data and LOB dynamics to
strategy development, execution, monitoring, and operational risk. Some venue
details and examples are dated, so use it to identify implementation questions
and then verify current exchange rules independently.

## Tick Data

Tick data are irregularly spaced, voluminous, and noisy. Quotes and trades
arrive randomly; bid-ask bounce can induce negative first-order
autocorrelation; data availability and quality differ by asset class and
venue.

Review:

- source, feed type, and coverage of the data;
- whether full depth, top of book, trades, or dealer quotes are available;
- timestamp resolution, clock synchronization, and ordering;
- corrections, cancellations, duplicate messages, and bad ticks;
- conversion from ticks to bars and information lost in aggregation;
- treatment of irregular arrival times.

## Orders And The Limit Order Book

Market orders offer immediacy with uncertain price. Limit orders offer price
control with uncertain execution and waiting risk. LOB shape and imbalance can
carry predictive information, but observability differs across centralized,
dealer, and dark markets.

Challenge any model that:

- treats a touched limit order as filled;
- ignores waiting and non-execution cost;
- assumes the visible book is total liquidity;
- applies centralized-book logic to decentralized markets;
- ignores order-type and time-in-force differences.

## Execution

Execution quality depends on order timing, slicing, market conditions,
benchmark choice, and impact. Aggressive execution reduces delay but can raise
impact; passive execution reduces explicit cost but adds fill and adverse-move
risk.

Require:

- an executable benchmark such as arrival price or decision price;
- explicit opportunity cost for unfilled orders;
- state-dependent impact and slippage;
- monitoring of confirmations and realized execution;
- reconciliation of expected and actual costs.

## System And Operational Risk

A high-frequency system must receive and archive data, apply models, generate
orders, enforce risk, receive acknowledgments, and monitor execution.
Unexpected trading costs, missing data, transmission failures, and software
errors can invalidate a strategy quickly.

Measure latency across the entire path rather than quoting one average:

- data publication and receipt;
- decoding and strategy decision;
- order transmission;
- exchange processing;
- acknowledgment and fill receipt.

## Reviewer Use

Use this source for an implementation reality check. Its strongest contribution
is the insistence that data, execution, and monitoring are part of the strategy.
Its weakest assumptions, such as coarse or dated venue descriptions, should
not be accepted without current rulebook evidence.

## Source Map

- HFT definitions and system lifecycle
- Order types, LOBs, and market making
- Chapter 9: working with tick data
- Execution algorithms and monitoring
- System implementation and operational risk

