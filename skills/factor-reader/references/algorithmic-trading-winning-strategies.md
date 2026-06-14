# Algorithmic Trading: Winning Strategies And Their Rationale

## Source

Ernie Chan, *Algorithmic Trading: Winning Strategies and Their Rationale*.

## Why This Source Matters

This source offers a practical backtesting and implementation lens. It
includes cross-sectional ranking strategies and repeatedly highlights
look-ahead bias, survivorship bias, data snooping, transaction costs,
short-sale constraints, regime shifts, and true out-of-sample tests.

It is not a substitute for academic asset-pricing inference. Use it to test
whether a reported factor portfolio could have been formed and traded with
the information and instruments available at the time.

## Cross-Sectional Portfolio Construction

Cross-sectional strategies rank assets by lagged returns or other variables
and form long-short portfolios from extreme ranks. Examples include
cross-sectional momentum and mean reversion, as well as fundamental and
statistical factors.

The source illustrates top-versus-bottom portfolios, overlapping holding
periods, and factor-ranked stock selection. These examples make several
review questions concrete:

- Was the rank observable before the trade?
- How were missing observations and ties handled?
- Was the universe known point-in-time?
- Did overlapping portfolios create serial correlation?
- Did the backtest rebalance at a feasible time and price?

The practical rank portfolio is evidence about a strategy construction, not
by itself evidence that the characteristic earns distinct risk-adjusted alpha.

## Backtest Biases

Look-ahead bias occurs whenever future information influences signal
construction, parameter choice, universe membership, or execution. Using the
same data to select parameters and report performance is especially
dangerous.

Survivorship bias can materially inflate equity strategy results. A current
index constituent list is not a valid historical universe. Delisted stocks,
bankruptcies, and historical membership must be represented.

Data-snooping bias grows as researchers try more instruments, parameters,
signals, and combinations. Strong in-sample performance should be followed by
a genuinely untouched test.

Published strategy examples can create a useful true out-of-sample period:
reconstruct the original rules without using post-publication data, then test
the subsequent period. Poor post-publication performance can reflect
overfitting, crowding, changing regimes, or higher implementation costs; the
test does not identify the cause by itself.

## Timing, Data, And Tradeability

Data timestamps must match the claimed implementation. Closing prices from
different markets can be asynchronous. Fundamental, holdings, news, and other
alternative data may arrive with substantial delays.

Short positions require borrow availability and may face bans or changing
constraints. A long-short spread that assumes every historical loser could be
shorted is not an implementable portfolio.

Transaction costs depend on the exact execution. Backtests that omit them
should not be used as net-performance evidence. Slow data release, such as
quarterly holdings, can create large slippage before the signal becomes
tradable.

## Regimes And Strategy Decay

Cross-sectional momentum and other strategies can perform very differently
through crises and subsequent periods. A strong average can conceal a severe
regime-specific loss or a long decay in edge.

Reviewers should separate:

- the signal's pre-publication discovery sample;
- a holdout selected before final specification;
- the post-publication period;
- crisis and non-crisis regimes;
- pre-cost and post-cost performance.

Regime shifts can invalidate relationships that appeared durable in the
training sample. Risk management may limit losses but does not prove the
factor remains predictive.

## Relation To Academic Factor Tests

Ranking and extreme-portfolio spreads are useful visual and economic
diagnostics. They should be complemented by:

- characteristic controls and independent double sorts;
- Fama-MacBeth or other cross-sectional regressions;
- contemporary factor-model alphas;
- multiple-testing controls;
- point-in-time data and universe reconstruction;
- implementation and post-publication evidence.

## Factor-Reader Diagnostics

- Does the universe include delistings and historical constituents?
- Are signals, fundamentals, and holdings lagged by their true availability?
- Were parameters chosen on the same period used for evaluation?
- Is the test truly out of sample, or merely labeled so?
- Are overlapping holdings and serially correlated returns handled?
- Could the short leg be borrowed?
- Are transaction costs, financing, and timing delays included?
- Does the factor survive crisis and post-publication periods?

## Source-Led Review Standard

Demand a backtest that could have been executed by an informed but
non-clairvoyant trader. Point-in-time data, untouched out-of-sample evidence,
shortability, realistic timing, costs, and regime analysis are prerequisites
for interpreting a cross-sectional spread as investable.
