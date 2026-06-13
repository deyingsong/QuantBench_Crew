# Option Volatility and Pricing: Options-Reader Distillation

Source: Sheldon Natenberg, *Option Volatility and Pricing: Advanced Trading
Strategies and Techniques*.

## Contents

- [Why this source matters](#why-this-source-matters)
- [Trader-centered valuation](#trader-centered-valuation)
- [Volatility reasoning](#volatility-reasoning)
- [Greeks and position risk](#greeks-and-position-risk)
- [Dynamic hedging](#dynamic-hedging)
- [Volatility spreads and relative value](#volatility-spreads-and-relative-value)
- [Model assumptions versus the real world](#model-assumptions-versus-the-real-world)
- [Skew and surface risk](#skew-and-surface-risk)
- [Volatility products](#volatility-products)
- [Options-reader review checklist](#options-reader-review-checklist)
- [Source map](#source-map)

## Why This Source Matters

Natenberg provides a trading-desk interpretation of option models. The useful
unit of analysis is not a formula in isolation but a position whose P&L changes
with spot, time, volatility, skew, financing, dividends, and hedge adjustments.

Use this source to test whether a paper's apparently attractive pricing or
hedging result survives the practical questions a market maker would ask:

- What risk is actually being bought or sold?
- Which inputs are observed and which are forecasts?
- How will the position be adjusted?
- What breaks when markets gap, costs rise, or the skew moves?

## Trader-Centered Valuation

### Theoretical Value Is Conditional

A model price is conditional on inputs and assumptions. It is not an objective
fact. For a trader, the uncertain input is usually future realized volatility.
Interest rates, dividends, borrow, and the forward also matter, but volatility
is typically the central judgment.

When a paper reports mispricing, ask:

- mispriced relative to which volatility forecast and surface convention?
- does the claimed edge exceed bid-ask, fees, financing, and hedge cost?
- is the edge robust to a plausible input range?
- is the comparison between like instruments and timestamps?

### Think in Forward Terms

Option pricing and moneyness should be anchored to the forward where
appropriate. Verify treatment of dividends, rates, stock borrow, and corporate
actions. An incorrect forward contaminates implied volatility, delta, skew,
and relative-value conclusions.

## Volatility Reasoning

### Separate Volatility Concepts

Do not use "volatility" without qualification. Distinguish:

- historical or realized volatility over a specified sampling interval;
- forecast future realized volatility over the option's life;
- Black-Scholes implied volatility backed out from an option price;
- forward volatility between two future dates;
- volatility of volatility;
- skew or smile changes across strike and maturity.

Historical volatility depends on sampling interval, lookback, annualization,
and return definition. Implied volatility is a price representation, not a
direct forecast or physical-law parameter.

### Compare Implied with Expected Realized Carefully

Buying options because implied volatility is below a forecast of realized
volatility is incomplete. P&L also depends on:

- path and hedge frequency;
- transaction costs;
- gaps and discrete rebalancing;
- skew and implied-volatility changes;
- entry and exit prices;
- whether the chosen options efficiently express the view.

The same volatility view can have very different outcomes in different
strikes, maturities, and structures.

### Forward Volatility Must Be Internally Consistent

The relation between term volatilities and forward volatility is variance-based,
not a simple arithmetic difference. A term-structure trade should identify the
forward interval being bought or sold and the assumptions needed to isolate it.

## Greeks and Position Risk

### Greeks Are Local Sensitivities

Delta, gamma, theta, vega, and rho describe local model behavior. They are not
guarantees about finite moves. Their usefulness depends on the model and the
size and path of the shock.

For a position or portfolio, require:

- aggregate Greeks, not just per-option Greeks;
- units and sign conventions;
- spot and volatility bump sizes;
- full-revaluation checks for finite shocks;
- cross-Greeks or surface sensitivities when material.

### Gamma and Theta Are a Tradeoff

Long gamma positions generally pay time decay and benefit from sufficiently
large realized movement. Short gamma positions generally collect theta and
lose on sufficiently large movement. The meaningful question is whether the
realized path and hedge process cover the theta paid or collected after costs.

Gamma becomes especially dangerous near expiration and near the money.
Gaps can dominate a model that assumes continuous price movement.

### Vega Is Not One-Dimensional

An option's vega measures sensitivity to an assumed volatility change. A real
surface can twist, steepen, flatten, or move differently by maturity. A single
parallel-vega number can hide large skew and term-structure exposure.

## Dynamic Hedging

### Economic Meaning

Dynamic delta hedging repeatedly trades the underlying to offset changing
directional exposure. For a long-gamma position, hedge adjustments tend to
buy low and sell high; for a short-gamma position, the reverse. Under ideal
model assumptions, the cumulative hedge process realizes the theoretical
value associated with the volatility input.

### Assumptions Behind the Textbook Result

The clean dynamic-hedging result assumes:

- continuous or sufficiently frequent rebalancing;
- correct model and volatility input;
- frictionless trading;
- unrestricted shorting and financing;
- known dividends and rates;
- no gaps beyond the model's distribution.

Real markets violate all of these. More frequent hedging reduces path variance
under the model but increases transaction costs. Less frequent hedging lowers
cost but leaves larger directional and gap exposure.

### How to Evaluate a Hedging Paper

Require the study to state:

- hedge instrument and execution price;
- rebalance rule: clock, delta band, cost-aware, or learned policy;
- handling of overnight and event gaps;
- financing, dividends, borrow, and fees;
- the volatility and surface used to compute Greeks;
- terminal unwind and exercise treatment;
- P&L attribution among option, hedge, carry, costs, and model error.

Evaluate the full distribution of hedge P&L. Mean error alone can conceal
unacceptable tails.

## Volatility Spreads and Relative Value

Spreads combine options to reshape delta, gamma, theta, and vega exposure.
Names such as straddle, strangle, butterfly, condor, ratio spread, calendar,
and diagonal are not sufficient descriptions. The exact strikes, maturities,
ratios, and hedge policy determine the position.

Assess a spread using:

- initial and stressed Greeks;
- payoff and P&L across spot-volatility scenarios;
- skew and term-structure exposure;
- liquidity and legging risk;
- margin for input error;
- adjustment and exit plan.

A "vega-neutral" or "delta-neutral" spread is neutral only at a point and under
a model. It can rapidly acquire exposure as spot, time, and the surface move.

## Model Assumptions Versus the Real World

Natenberg explicitly challenges the standard assumptions:

- markets are frictionless;
- interest rates and volatility are constant;
- trading is continuous;
- volatility is independent of the underlying price;
- terminal prices are lognormally distributed.

Observed return distributions exhibit more small moves and more extreme moves
than a normal model predicts, with fewer intermediate moves. Equity volatility
often rises as prices fall. Near-expiration gaps can make model values and
deltas unreliable.

Use a model as a disciplined decision tool, but do not confuse its precision
with correctness. A more complex model may replace one uncertain input with
several uncertain inputs. Demand evidence that added complexity improves the
decision that matters.

## Skew and Surface Risk

### Interpret the Skew

Implied volatility differs by strike because the marketplace does not treat the
Black-Scholes distribution as adequate. Equity markets commonly show higher
implied volatility at lower strikes. Potential explanations include:

- demand for downside protection and supply of covered calls;
- negative spot-volatility dependence;
- asymmetric tail risk and crash fear.

These explanations can coexist. A paper should not infer a unique causal story
from the skew alone.

### Specify the Surface-Movement Convention

Risk changes depending on whether the skew is assumed to be:

- sticky strike;
- sticky delta or moneyness;
- shifted with spot;
- shifted with the at-the-money volatility;
- governed by a parametric or stochastic-surface model.

The convention affects delta, gamma, vega, and exotic prices. A hedge evaluated
under the same frozen convention used to generate the data is not a convincing
test of real surface risk.

### Include Skew and Curvature Sensitivities

Large positions can be sensitive to changes in skew slope and curvature even
when aggregate vega is near zero. Risk reversals and butterflies are common
ways to express or hedge these dimensions, but their neutrality changes over
time.

For surface studies, require:

- coordinate system: strike, log-moneyness, forward moneyness, or delta;
- interpolation and extrapolation method;
- no-arbitrage controls;
- term-structure treatment;
- risk under slope, curvature, and localized shocks.

## Volatility Products

Variance exposure is not the same as volatility exposure. A strip of options
weighted across strikes can replicate variance under ideal assumptions.
Because volatility is the square root of variance, constant variance exposure
does not produce constant volatility exposure.

Volatility and variance products introduce additional practical issues:

- strike truncation and discrete available options;
- bid-ask cost across many legs;
- delta hedging and gamma exposure;
- settlement methodology;
- mismatch between the index and the tradable hedge;
- term-structure and mean-reversion behavior.

Do not treat VIX spot, VIX futures, VIX options, and variance swaps as
interchangeable. Their underlyings, settlement rules, and dynamics differ.

## Options-Reader Review Checklist

- Is every volatility quantity precisely defined?
- Is the forward and dividend treatment correct?
- Is apparent mispricing larger than all implementation costs?
- Are Greeks aggregated and checked with full revaluation?
- Are gamma-theta and realized-implied tradeoffs explained?
- Does hedging P&L include execution, financing, dividends, and borrow?
- Is hedge frequency chosen ex ante and sensitivity-tested?
- Are gaps, events, and overnight moves represented?
- Does the study model skew and term-structure movement?
- Are surface-coordinate and stickiness assumptions explicit?
- Are spreads described by exact legs and ratios?
- Are position risks evaluated after spot, time, and volatility changes?
- Are volatility products matched to their actual tradable hedges?
- Does model complexity improve a practical pricing or hedging outcome?

## Source Map

- Chapters 5-6: theoretical pricing inputs and volatility interpretation.
- Chapters 7-9: Greeks, dynamic hedging, and second-order position risk.
- Chapters 10-13: spreads, volatility structures, and risk considerations.
- Chapter 17: hedging with options.
- Chapters 20-21: volatility forecasting, forward volatility, and position
  analysis.
- Chapters 23-24: model limitations, non-normality, skew, and surface risk.
- Chapter 25: realized and implied volatility contracts and replication.

