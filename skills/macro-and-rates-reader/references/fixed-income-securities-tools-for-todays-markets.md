# Fixed Income Securities: Tools For Today's Markets

Source: Bruce Tuckman and Angel Serrat, *Fixed Income Securities: Tools for
Today's Markets*.

## Why This Source Matters

Tuckman and Serrat combine fixed-income valuation with market plumbing,
monetary-policy implementation, liquidity, term-structure interpretation, and
instrument-specific hedging. Use this source to prevent a macro/rates paper
from treating the yield curve as a frictionless set of expectations.

## Curves And No-Arbitrage

Swap or par rates, spot rates, discount factors, and forward rates are
different representations of a term structure. Bootstrapping links them
through no-arbitrage, but the construction depends on:

- instrument conventions and payment dates;
- collateral and discounting curve;
- interpolation and extrapolation;
- liquidity and credit differences;
- data timing and stale observations.

Always identify the exact curve. A Treasury, OIS, swap, credit, or inflation
curve answers a different question.

## Forwards Are Not Pure Expectations

The book decomposes long-term forward rates into:

- expectations of future rates;
- risk premium;
- convexity effects.

Therefore, an upward forward curve does not directly establish expected policy
tightening, and a declining long forward rate does not directly establish
expected easing. Convexity and time-varying term premia can materially alter
the inference.

Review:

- whether the paper equates forwards with expectations;
- how term premium is estimated or assumed;
- whether convexity matters at long maturities;
- whether the result changes under alternative decomposition models.

## Rate Risk And Hedging

DV01 and duration are local first-order measures. Convexity improves estimates
for larger moves and reveals volatility exposure. Key-rate, partial, and
forward-bucket sensitivities are needed when curve moves are not parallel.

Hedges are instrument- and curve-specific. Treasury, futures, swaps, and bonds
can carry basis, financing, liquidity, delivery-option, and credit differences.
Matching total DV01 alone does not establish a robust hedge.

## Monetary-Policy Plumbing

Policy implementation changes across operating regimes. In a scarce-reserve
system, central banks influence overnight rates differently than in an
abundant-reserve or floor system using administered rates, reverse repos, and
standing facilities. Repo markets, balance-sheet constraints, and regulation
can weaken or distort transmission.

For policy-event research, state:

- operating framework and target rate;
- reserve regime;
- relevant administered rates and facilities;
- collateral and repo conditions;
- concurrent balance-sheet policy;
- whether the same reaction-function interpretation applies before and after
  framework changes.

## Negative Rates, QE, And Yield-Curve Control

Negative policy rates, quantitative easing, and yield-curve control alter
pricing, bank incentives, term premia, and supply-demand conditions. Policy can
directly affect the assets used to infer expectations. Treat such periods as
distinct regimes rather than tail observations from a stable model.

## Liquidity

Fixed-income liquidity varies by asset class, issue age, size, credit quality,
trade size, and market state. Electronic liquidity for small trades does not
guarantee capacity for large trades. ETF liquidity can diverge from underlying
bond liquidity during stress.

## Reviewer Diagnostics

- Is the curve source appropriate to the claim?
- Are policy-rate changes confused with changes in funding or collateral
  conditions?
- Are forward rates treated as forecasts without term-premium and convexity
  caveats?
- Are hedges exposed to basis, financing, delivery, or liquidity risk?
- Are normal-time liquidity measures used to make stress-period claims?
- Are negative-rate, QE, and abundant-reserve periods pooled with conventional
  regimes without interaction terms or subsamples?

## Reviewer Use

Use this source for curve construction, expectations inference, monetary-policy
transmission, repo, swaps, hedging, and liquidity. Its main discipline is to
connect macro interpretation to the instruments and institutions that generate
the observed rates.

## Source Map

- Overview: market structure, policy regimes, and liquidity
- Curves: swap, spot, forward rates, and discount factors
- DV01, duration, convexity, and multifactor hedging
- Expectations, risk premium, convexity, and term-structure shape
- Repo, futures, swaps, credit, mortgages, and options

