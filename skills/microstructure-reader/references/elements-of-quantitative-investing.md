# Elements Of Quantitative Investing

Source: Giuseppe A. Paleologo, *The Elements of Quantitative Investing*.

## Why This Source Matters

This source connects predictive research to portfolio construction,
transaction costs, capacity, implementation, and production discipline. It is
not primarily an HFT text; use it to challenge whether a statistically strong
microstructure signal remains economically useful after turnover, impact, and
realistic validation.

## Research And Backtesting Discipline

The book emphasizes:

- high-quality, point-in-time data;
- explicit prevention of look-ahead and survivorship bias;
- predefined research protocols;
- walk-forward testing;
- production settings that match research settings;
- calibrated transaction-cost models.

For microstructure work, "point in time" includes not only the feature values
but when the feed, book update, and venue response became available to the
strategy.

## Turnover Is A Production Property

Turnover is not only an intrinsic characteristic of a signal. It depends on
portfolio construction, rebalance frequency, constraints, optimization,
universe changes, and execution. Two implementations of the same forecast can
have materially different capacity and cost.

Review:

- turnover caused by signal changes versus model or universe changes;
- whether transaction-cost penalties are inside the optimizer;
- sensitivity to rebalance frequency;
- whether constraints create concentrated or abrupt trades;
- whether backtest and production optimizers are identical.

## Market Impact And Execution

Expected transaction cost can be decomposed into spread, temporary impact, and
permanent impact. Implementation shortfall compares the arrival price with the
realized average execution price. Liquidity includes depth, breadth, and
resilience.

Impact parameters must be calibrated against realized executions and should
vary with market conditions. A cost model used descriptively in a backtest may
become endogenous when the strategy uses that same model to choose trades.

## Capacity

Capacity is the scale beyond which increasing capital and trade size destroy
economic returns. It is not captured by average daily volume alone.

Require:

- net performance over a scale curve;
- impact calibrated for the strategy's participation and horizon;
- concentration and liquidity-regime stress;
- interaction between crowding, turnover, and decay;
- capacity estimates by instrument and venue.

## Reviewer Diagnostics

- Are execution costs omitted from any claimed improvement?
- Is the impact model calibrated to a different strategy or regime?
- Does the strategy's predicted return arrive before it can be executed?
- Are backtest decisions reproducible using only contemporaneous data?
- Does performance survive conservative costs and larger trade sizes?
- Are comparisons made at matched risk, turnover, and capacity?

## Reviewer Use

Use this source to connect an HFT or execution result to investment economics.
A paper has not established value merely by predicting the next price move; it
must show that the signal can be transformed into scalable net P&L under a
credible production process.

## Source Map

- Backtesting best practices and protocol
- Model and portfolio turnover
- Capacity and trading Sharpe
- Market impact, implementation shortfall, and optimal execution

