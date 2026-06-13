# De Jong-Rindi Microstructure Of Financial Markets

Source: Frank de Jong and Barbara Rindi, *The Microstructure of Financial
Markets*.

## Why This Source Matters

This source connects classic microstructure theory to empirical estimation.
It is especially useful for reviewing spread decomposition, price-impact
measurement, price discovery, transparency, and fragmented markets.

## Mechanism Map

- Inventory models compensate liquidity suppliers for holding unwanted risk.
- Information models compensate them for losses to better-informed traders.
- Fixed and order-processing costs can also contribute to spreads.
- Strategic traders internalize their own price impact and trade less
  aggressively.
- Market organization changes participant behavior and therefore market
  quality.

The book repeatedly shows that similar reduced-form patterns can arise from
different mechanisms. Identification requires more than observing signed
trades and returns.

## Empirical Measures

Useful distinctions include:

- quoted, effective, and realized spreads;
- immediate versus long-run price impact;
- transitory inventory effects versus permanent information effects;
- depth as the inverse of price sensitivity;
- trade-level and lower-frequency liquidity proxies;
- price discovery across multiple venues.

The usual identification idea is that information has a permanent price
effect, while inventory pressure eventually reverses. This is useful but
conditional: correlated order flow, delayed information, cross-venue
adjustment, and changing fundamentals can violate the simple separation.

## Data And Estimation Diagnostics

Empirical microstructure work normally requires intraday trades and quotes.
Review:

- trade-sign classification and its error rate;
- quote/trade timestamp alignment;
- whether midpoint returns or transaction returns are used;
- serial dependence caused by order splitting;
- variation in trade size;
- whether inventory is observed or inferred;
- treatment of opening, closing, auctions, and overnight changes;
- cross-venue synchronization and consolidated versus local quotes.

Do not interpret one coefficient as an adverse-selection share unless the
model's timing and decomposition assumptions are credible.

## Market-Design Diagnostics

Transparency and fragmentation have ambiguous effects. Transparency may
reduce information asymmetry but can discourage displayed liquidity.
Consolidation creates liquidity externalities, while fragmentation can improve
competition or allow traders to reduce impact.

Ask:

- Which participants can see which orders and when?
- Is the market anonymous?
- Are trades and quotes consolidated?
- Can orders route across venues?
- Does the study capture dark or off-book activity?
- Did tick size, priority, or disclosure rules change during the sample?

## Reviewer Use

Use this source when a paper estimates transaction costs, decomposes spreads,
or claims a structural market-quality effect. Demand a clear bridge from the
theoretical friction to the estimator and then to the data-generating process.
Test whether the conclusion survives alternative spread and impact measures.

## Source Map

- Chapters 2-5: rational expectations, adverse selection, and inventory theory
- Chapter 6: empirical transaction-cost and spread models
- Chapters 7-9: liquidity pricing, dynamic models, and price discovery
- Chapter 10: transparency, consolidation, and fragmentation

