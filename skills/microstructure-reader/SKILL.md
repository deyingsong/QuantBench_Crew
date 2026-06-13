---
name: microstructure-reader
description: Read and review HFT, market-microstructure, market-impact, and execution research as a domain expert, covering tick and message data, limit-order books, liquidity, adverse selection, inventory, market making, optimal execution, latency, matching rules, fragmentation, and venue design. Use when Scout detects a paper whose central contribution or evidence concerns high-frequency trading, order flow, limit-order placement, transaction costs, price impact, execution algorithms, exchange mechanics, liquidity provision, or market quality; invoke from Reader for source-grounded extraction and from Reviewer for adversarial domain critique.
---

# Microstructure Reader

Analyze microstructure research as an interaction among traders, messages,
matching rules, venues, and market states. Reconstruct what the strategy knew,
sent, and received before accepting a statistical or economic result.

## Routing

Treat a paper as in-domain when its central question depends on one or more of:

- trades, quotes, order flow, message data, or limit-order-book dynamics;
- HFT, market making, liquidity provision, or adverse selection;
- transaction costs, market impact, optimal execution, or order placement;
- latency, queue priority, matching rules, fees, or exchange architecture;
- fragmentation, dark trading, transparency, tick size, or market quality.

Do not route a paper merely because it trades frequently or includes
transaction costs. The microstructure mechanism, data, venue, or execution
problem must be central.

When invoked by Reader, reconstruct the paper faithfully before criticizing
it. When invoked by Reviewer, challenge the result using the paper, run
artifacts, and domain diagnostics. Preserve the caller's requested schema.

## Reference Router

Load only the references needed for the task:

- For foundational inventory, information, strategic-trading, and
  market-design mechanisms, read
  [market-microstructure-theory.md](references/market-microstructure-theory.md).
- For empirical spread decomposition, price impact, price discovery,
  transparency, and fragmentation, read
  [microstructure-of-financial-markets.md](references/microstructure-of-financial-markets.md).
- For liquidity dimensions, policy, dark trading, transparency, and venue
  design, read
  [market-liquidity-theory-evidence-policy.md](references/market-liquidity-theory-evidence-policy.md).
- For HFT heterogeneity, speed races, cross-venue connectivity, and welfare,
  read
  [economics-of-high-frequency-trading.md](references/economics-of-high-frequency-trading.md).
- For inventory-aware market-making baselines, read
  [avellaneda-stoikov-limit-order-book.md](references/avellaneda-stoikov-limit-order-book.md);
  for directional bets and terminal inventory penalties, also read
  [fodra-labadie-market-making.md](references/fodra-labadie-market-making.md).
- For optimal execution, impact, order-flow signals, and control methods, read
  [algorithmic-and-high-frequency-trading.md](references/algorithmic-and-high-frequency-trading.md).
- For noisy, irregular, asynchronous tick data and volatility or jump
  estimation, read
  [high-frequency-financial-econometrics.md](references/high-frequency-financial-econometrics.md).
- For tick-data practice, order types, execution monitoring, and system risk,
  read
  [high-frequency-trading-practical-guide.md](references/high-frequency-trading-practical-guide.md).
- For gateways, book building, matching rules, OMS state, latency, and
  production feasibility, read
  [developing-high-frequency-trading-systems.md](references/developing-high-frequency-trading-systems.md).
- For capacity, turnover, impact, and institutional backtesting, read
  [elements-of-quantitative-investing.md](references/elements-of-quantitative-investing.md).
- For research-process discipline, walk-forward testing, costs, and
  incubation, read
  [building-winning-algorithmic-trading-systems.md](references/building-winning-algorithmic-trading-systems.md).

Read multiple references when a conclusion connects theory, empirical
identification, execution, and production mechanics.

## Workflow

### 1. Establish Evidence And Venue Scope

Record the paper, appendices, code, data dictionary, exchange rulebook,
message schema, sample dates, instruments, venues, and run artifacts. Label
missing evidence. Separate explicit paper statements from inference.

### 2. Define The Claim And Mechanism

Identify the claimed friction or mechanism: information, inventory, search,
latency, queue priority, competition, impact, fragmentation, or market design.
State the affected traders, market-quality dimension, and proposed economic
channel.

### 3. Reconstruct The Event Pipeline

Map raw feed messages into trades, quotes, books, features, decisions, orders,
acknowledgments, fills, cancels, rejects, positions, and P&L. Record timestamps,
clock domains, ordering rules, gaps, corrections, and synchronization choices.

### 4. Audit Venue Mechanics

Document tick and lot size, matching priority, order types, time in force,
maker/taker economics, auctions, halts, throttles, hidden liquidity, and
cancel/replace behavior. Verify current and sample-period rules.

### 5. Audit Fills, Latency, And Adverse Selection

Never infer a fill merely because price touched an order. Evaluate queue
position, competing flow, partial fills, missed fills, end-to-end latency,
stale quotes, cancel failures, and post-fill markouts. Treat fill probability
and toxicity jointly.

### 6. Audit Impact And Execution Economics

Identify spread, fees, rebates, temporary and permanent impact, opportunity
cost, terminal liquidation, and benchmark price. Determine whether impact is
causal, informational, mechanical, or confounded by other flow.

### 7. Audit Models And Identification

Extract state variables, dynamics, objectives, controls, constraints,
estimators, and calibration. Connect each assumption to an observable fact.
Challenge whether the empirical design distinguishes information, inventory,
public news, and mechanical price pressure.

### 8. Validate Across Time, Venue, And Regime

Test or request tests across instruments, venues, liquidity buckets,
volatility states, spreads, participation rates, intraday periods, auctions,
stress events, and rule changes. Use chronological out-of-sample evaluation
and realistic production timing.

### 9. Issue The Assessment

Separate:

- what the paper establishes;
- what depends on model, data, or venue assumptions;
- what is statistically unidentified or operationally infeasible;
- where results fail to generalize;
- which decisive test could change the conclusion.

## Domain Diagnostics

### Tick And Message Data

- Are feed source, message schema, timestamps, sequence handling, and clock
  synchronization documented?
- Are corrections, duplicates, gaps, crossed markets, and auctions handled?
- Is the feature available at decision time?

### Market Making And Order Placement

- Are fills queue-, latency-, and state-aware?
- Are inventory P&L, spread capture, rebates, alpha, and markouts separated?
- Does the strategy survive toxic flow and executable liquidation?

### Impact And Execution

- Are temporary, permanent, informational, and mechanical effects separated?
- Are unfilled quantity and opportunity cost included?
- Does net performance survive scale, participation, and stress?

### Causal And Market-Design Claims

- Does the design isolate the rule, speed, or venue change from concurrent
  changes?
- Are migration, spillovers, and cross-venue effects measured?
- Which traders gain or lose, and by which market-quality measure?

### Generalization

- Do findings survive other venues, matching rules, fee schedules, and
  liquidity regimes?
- Are sample-period institutional details verified rather than assumed?
- Are model parameters re-estimated rather than transported unchanged?

## Output Discipline

When no stricter caller schema is supplied, return:

1. `domain_fit`: why the microstructure expert was invoked;
2. `claim_and_mechanism`: central claim, affected traders, and channel;
3. `data_and_venue`: feeds, event construction, rules, and sample scope;
4. `method_reconstruction`: model, estimator, strategy, or identification;
5. `domain_findings`: strengths and issues ordered by consequence;
6. `execution_reality`: fills, latency, costs, impact, and operational limits;
7. `generalization_and_decisive_tests`: regime risks and tests that could
   change the verdict;
8. `confidence`: confidence and missing evidence.

## Guardrails

- Do not invent exchange rules, data cleaning, queue position, or order states.
- Do not infer fills from quote touches or assume cancels are instantaneous.
- Do not treat displayed depth as total or fully executable liquidity.
- Do not equate liquidity provision with uninformed trading or liquidity
  taking with informed trading.
- Do not call impact permanent without a justified horizon and counterfactual.
- Do not transport parameters or conclusions across venues and regimes without
  evidence.
- Do not let gross P&L outrank fees, impact, missed fills, adverse selection,
  capacity, and terminal liquidation.
- Do not issue investment advice.

