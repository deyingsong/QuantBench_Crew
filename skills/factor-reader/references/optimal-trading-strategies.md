# Optimal Trading Strategies

## Source

Robert Kissell, Morton Glantz, and Roberto Malamut, *Optimal Trading
Strategies: Quantitative Approaches for Managing Market Impact and Trading
Risk*.

## Why This Source Matters

This book is an implementation reference. It explains why a paper portfolio
and a realized factor portfolio can differ materially through delay, spread,
market impact, timing risk, incomplete execution, and opportunity cost.

It does not establish whether a characteristic predicts the cross-section of
returns. Use it after the statistical claim has been reconstructed, to decide
whether the claimed alpha can survive trading.

## Transaction-Cost Decomposition

The source separates visible costs from less transparent costs. Relevant
components include:

- commissions, taxes, fees, and spreads;
- delay and price appreciation or drift;
- temporary and permanent market impact;
- timing risk;
- opportunity cost from unexecuted shares.

Market impact is price movement caused by the order through liquidity demand
and information leakage. Timing risk is uncertainty around execution cost,
driven by price volatility and intraday volume uncertainty. Opportunity cost
arises when liquidity or adverse prices prevent completion.

A factor paper that subtracts only commissions or half-spreads materially
understates implementation drag for large, fast, illiquid, or crowded trades.

## Implementation Shortfall

Implementation shortfall compares the return of a frictionless paper
portfolio with the return of the actual portfolio. The paper portfolio assumes
instantaneous execution in unlimited size without transaction costs.

Expanded implementation shortfall can attribute costs to delay, execution,
opportunity cost, and visible charges. This is preferable to judging execution
only against an arbitrary benchmark such as VWAP or the close.

For factor portfolios, define:

- the investment-decision timestamp;
- the price at decision, order release, entry, execution, and completion;
- residual or unexecuted shares;
- the terminal valuation and unwind;
- the benchmark against which implementation drag is measured.

Without these timestamps, a backtest cannot reliably separate signal return
from execution luck or delay.

## Cost-Risk Trade-Off

Trading faster reduces exposure to timing risk and signal decay but tends to
increase market impact. Trading slower reduces participation and impact but
increases exposure to drift, volatility, and opportunity cost.

Pre-trade estimates should be conditional on order size, liquidity, market
conditions, and execution strategy. Cost is a distribution, not one universal
basis-point haircut.

The optimal execution schedule depends on the manager's objective and risk
aversion. A short-lived factor may require rapid trading that consumes much of
its gross alpha; a slow factor may tolerate lower participation and lower
impact.

## Implications For Factor Research

Portfolio formation and execution should be integrated. A characteristic can
look attractive in a frictionless decile spread but fail when:

- turnover is high relative to predictive half-life;
- returns occur near reconstitution or announcement dates;
- the signal concentrates in small or low-volume stocks;
- the short leg is less liquid than the long leg;
- many managers trade the same names at the same time;
- incomplete fills leave unintended factor exposures;
- the paper uses closing prices that could not be achieved at scale.

Cost models should use contemporaneous liquidity and volatility, not a single
full-sample average. Stress periods require separate assumptions.

## Post-Trade Evaluation

A benchmark comparison alone can be misleading because it may ignore market
conditions, price trend, and the chosen implementation strategy. Evaluate
whether cost was reasonable conditional on the opportunity and constraints.

For an empirical factor paper or replication, useful post-trade evidence
includes:

- predicted versus realized cost;
- implementation shortfall by rebalance;
- cost by size, liquidity, side, and market state;
- completion rates and opportunity cost;
- sensitivity to participation limits and delayed entry;
- paper-versus-realized factor exposure.

## Factor-Reader Diagnostics

- Is reported alpha gross, net of simple costs, or net of a realistic
  strategy-conditional cost model?
- Are decision and execution timestamps feasible?
- Does faster implementation erase alpha through impact?
- Does slower implementation erase alpha through decay or opportunity cost?
- Are capacity and crowding modeled through order size and liquidity?
- Are unexecuted shares and short-side constraints represented?
- Are cost assumptions stable across liquidity regimes?

## Source-Led Review Standard

Do not call a factor investable because a frictionless long-short portfolio
earns a spread. Translate the signal into orders, model the cost-risk
trade-off, and assess performance with implementation shortfall and realistic
completion assumptions.
