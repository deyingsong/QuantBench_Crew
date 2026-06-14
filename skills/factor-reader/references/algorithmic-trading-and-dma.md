# Algorithmic Trading And DMA

## Source

Barry Johnson, *Algorithmic Trading & DMA: An Introduction to Direct Access
Trading Strategies*.

## Source Limitation

The attached PDF is an image-only scan whose text extraction and OCR are
largely unreadable. This note therefore uses the source conservatively: it
captures the book's reliably identifiable domain contribution as an
algorithmic-execution and direct-market-access reference, without attributing
unverified detailed prescriptions or formulas.

This source should not be used as evidence for cross-sectional asset-pricing
inference, double sorts, Fama-MacBeth regressions, or factor-model alpha.

## Why This Source Matters

A factor paper eventually becomes a stream of orders. Direct market access,
order types, execution algorithms, venue mechanics, and pre- and post-trade
controls determine whether the theoretical factor portfolio can be reached at
the prices assumed by the study.

Use this source when reviewing execution feasibility, especially for
high-turnover, small-cap, short-lived, or crowded factor signals.

## Execution Translation

Translate every portfolio rebalance into an executable order problem:

- target shares or notional by name;
- side, urgency, and signal half-life;
- order size relative to available liquidity;
- permissible order types and execution algorithms;
- venue access and trading-session assumptions;
- cancellation, partial-fill, and residual-position handling;
- pre-trade risk limits and post-trade reconciliation.

A close-to-close factor return is not automatically attainable. The strategy
must specify when the signal becomes known, when orders can be submitted, and
what prices and liquidity are available after that point.

## Direct-Market-Access Lens

DMA reduces some intermediation and gives greater control over order
submission, but it does not remove spreads, queueing, adverse selection,
latency, market impact, venue fragmentation, or operational risk.

For a factor portfolio, examine whether the assumed execution:

- depends on immediate fills at the displayed price;
- ignores partial fills or queue priority;
- assumes all names can trade simultaneously at the close;
- overlooks auction, halt, or short-sale restrictions;
- treats routing and venue choice as irrelevant;
- assumes execution behavior is unchanged across market regimes.

## Algorithm Choice And Benchmarking

Execution algorithms optimize different objectives. A schedule targeting a
volume benchmark, a participation rate, a closing auction, or rapid
completion can produce different realized costs and exposures.

Reviewers should align the execution algorithm with the factor's economics:

- fast-decaying signals require urgency but may pay more impact;
- slow factors can trade patiently but remain exposed to drift;
- index-like or rebalance-date strategies may face concentrated crowding;
- illiquid short legs may be impossible to complete symmetrically.

Execution quality should be assessed against the decision objective and
market conditions, not only against a convenient price benchmark.

## Controls And Operational Reality

An implementable factor strategy requires:

- pre-trade limits on size, price, exposure, and participation;
- short-sale and borrow controls;
- handling for rejects, disconnects, halts, and stale data;
- prevention of duplicate or runaway orders;
- reconciliation between target, order, fill, and final portfolio;
- surveillance of realized costs and unintended exposures.

Operational failures can create returns and risks unrelated to the factor
claim. A paper that assumes frictionless target attainment omits this layer.

## Factor-Reader Diagnostics

- At what exact time is the signal known and executable?
- Which order type or algorithm reaches the target portfolio?
- Are assumed prices available after signal formation?
- How are partial fills and unexecuted names handled?
- Does venue or auction concentration create crowding?
- Are short-sale, borrow, halt, and rejection rules modeled?
- Does the realized portfolio preserve the intended factor neutrality?
- Are execution assumptions stress-tested across liquidity regimes?

## Source-Led Review Standard

Treat the factor portfolio as a target, not an achieved position. Require an
explicit path from target weights to orders and fills, with realistic market
access, controls, and reconciliation. Because the attached scan is not
reliably machine-readable, consult the original PDF directly before citing
book-specific details beyond this execution-domain lens.
