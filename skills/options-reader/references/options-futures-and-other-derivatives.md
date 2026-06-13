# Options, Futures, and Other Derivatives: Options-Reader Distillation

Source: John C. Hull, *Options, Futures, and Other Derivatives*.

## Contents

- [Why this source matters](#why-this-source-matters)
- [No-arbitrage foundations](#no-arbitrage-foundations)
- [Pricing-model hierarchy](#pricing-model-hierarchy)
- [Greeks and hedging](#greeks-and-hedging)
- [Data-driven hedging](#data-driven-hedging)
- [Volatility smiles and surfaces](#volatility-smiles-and-surfaces)
- [Exotic options](#exotic-options)
- [Numerical methods](#numerical-methods)
- [Advanced volatility models and model risk](#advanced-volatility-models-and-model-risk)
- [Risk and implementation controls](#risk-and-implementation-controls)
- [Options-reader review checklist](#options-reader-review-checklist)
- [Source map](#source-map)

## Why This Source Matters

Hull supplies the broad benchmark toolkit for derivatives research. Use it to
verify whether a paper respects basic no-arbitrage relationships, chooses a
pricing method suited to the payoff, computes and interprets Greeks correctly,
and understands the difference between calibrating vanilla options and pricing
path-dependent exotics.

The source is especially useful as a baseline. A sophisticated method should
be compared with the simplest defensible analytic, tree, Monte Carlo, finite
difference, or static-replication alternative.

## No-Arbitrage Foundations

Before evaluating a model, verify the contract and market inputs:

- payoff, exercise style, settlement, multiplier, and monitoring;
- spot, forward, rates, dividends, borrow, and currency treatment;
- put-call parity and lower/upper bounds;
- early-exercise logic;
- collateral, funding, and valuation-adjustment assumptions where relevant.

Risk-neutral valuation is not a statement that investors are risk neutral in
the real world. It is a pricing construction under no-arbitrage assumptions.
The drift used for pricing and the drift forecast under the physical measure
serve different purposes.

## Pricing-Model Hierarchy

### Black-Scholes-Merton as Baseline

Black-Scholes-Merton provides a transparent benchmark under continuous
lognormal diffusion, constant volatility, frictionless trading, and continuous
hedging. Use it to check:

- price monotonicity and parity;
- implied volatility;
- analytic Greeks;
- limiting and special cases;
- whether a more complex method adds value.

Do not accept Black-Scholes-Merton as a complete description of equity-option
risk. Observed equity skews, stochastic volatility, jumps, costs, and discrete
hedging violate its assumptions.

### Trees

Binomial and trinomial trees are natural for American exercise and many
state-dependent claims. Their validity depends on:

- matching drift and volatility correctly;
- time-step convergence;
- dividend and exercise handling;
- barrier alignment and interpolation;
- state-space design for path dependence.

### Monte Carlo

Monte Carlo is natural for multi-factor and path-dependent payoffs but requires
careful treatment of:

- discretization bias;
- random-number quality and seeds;
- variance reduction;
- correlated factors;
- early exercise;
- confidence intervals and convergence.

### Finite Differences

Finite differences solve the pricing PDE on a grid and can handle early
exercise and barriers. Assess domain bounds, grid resolution, stability,
boundary conditions, and convergence.

## Greeks and Hedging

### Delta Hedging Is Approximate in Practice

Delta hedging protects against small underlying moves under the model.
Rebalancing at discrete intervals introduces hedge error. More frequent
rebalancing reduces model-implied hedge dispersion but increases trading cost.

Require a hedging paper to compare at least:

- unhedged or simple baseline;
- fixed-frequency delta hedge;
- alternative frequencies or bands;
- cost-aware policy;
- full P&L distribution.

### Gamma and Vega Require Options

The underlying has zero gamma and vega. Gamma or vega hedging requires traded
options or other nonlinear instruments. Making a portfolio gamma neutral
changes delta; making it both gamma and vega neutral generally requires at
least two option instruments.

Gamma and vega neutrality are temporary and local. Monitor how quickly
exposure reappears and the cost of restoring neutrality.

### Scenario Analysis Complements Greeks

Greeks are local derivatives. Scenario analysis and full revaluation are needed
for large spot moves, volatility shifts, skew changes, time passage, and joint
shocks. A robust risk report includes both.

### Practical Limits

Dealers may rebalance delta daily or more often, but continuously maintaining
gamma and vega neutrality is usually infeasible. Real hedging also faces
transaction costs, liquidity, gaps, and model error. A paper that assumes away
these constraints should label its result as an idealized benchmark.

## Data-Driven Hedging

Hull presents reinforcement learning as a framework for sequential hedging
with transaction costs and other frictions. A data-driven hedge should not be
judged only by lower in-sample P&L variance.

Require:

- clearly specified state, action, reward or loss, and constraints;
- an economic baseline such as Black-Scholes delta;
- costs included during training and testing;
- time-based out-of-sample evaluation;
- testing across volatility and liquidity regimes;
- controls against look-ahead and simulator leakage;
- tail-risk, turnover, and stability reporting;
- behavior under model misspecification.

If training and evaluation use the same simulator and assumptions, the model
may only have learned that simulator's hedge. Test it under alternative
processes, surface dynamics, jumps, and cost schedules.

## Volatility Smiles and Surfaces

### Surface Meaning

An implied-volatility surface maps option prices into volatility by strike or
moneyness and maturity. For European calls and puts with the same strike and
maturity, put-call parity implies the same implied volatility when inputs are
consistent.

Equity options typically show a downward skew: low-strike options have higher
implied volatility. This corresponds to a risk-neutral distribution with a
heavier left tail and lighter right tail than a comparable lognormal
distribution. Explanations include negative spot-volatility dependence,
leverage, volatility feedback, and crash fear.

### Coordinate and Interpolation Choices

Surface representation may use strike, spot moneyness, forward moneyness, or
delta. Specify the choice. Reliable quotes populate only part of the surface;
the rest depends on interpolation and extrapolation.

Check:

- crossed, stale, and illiquid quote filters;
- use of bid, ask, mid, or last;
- smoothing and interpolation;
- calendar and butterfly arbitrage;
- wing extrapolation;
- surface stability through time.

### Minimum-Variance Delta

When implied volatility and spot are correlated, the Black-Scholes delta may
not minimize hedge variance. A minimum-variance delta incorporates the
empirical relation between spot moves and implied-volatility moves. Evaluate
it out of sample and after costs; it is a statistical hedge, not a universal
identity.

### The Role of the Model

Vanilla options reveal risk-neutral marginal distributions by maturity, but
they do not uniquely determine joint dynamics between dates. This distinction
is decisive for exotics and hedging.

## Exotic Options

Hull surveys packages, forward starts, cliquets, compound and chooser options,
barriers, binaries, lookbacks, shouts, Asians, exchange options, multi-asset
options, and volatility/variance swaps.

Classify an exotic by its main difficulty:

- early exercise;
- discontinuous payoff;
- barrier or monitoring dependence;
- averaging or extrema;
- multiple assets and correlation;
- future strike or reset;
- volatility or variance exposure.

### Hedging Difficulty Varies by Payoff

Asian options can become easier to hedge as more observations fix the final
average. Barrier options can become extremely difficult near the barrier
because value and delta may change discontinuously when the barrier is hit.
Binary options also concentrate risk near the discontinuity.

Require scenario analysis around payoff discontinuities, observation dates,
and settlement conventions.

### Static Options Replication

Some exotics can be hedged with a portfolio of vanillas chosen to match
boundary values. Static or quasi-static replication reduces frequent
rebalancing but depends on:

- availability and liquidity of the required strikes and maturities;
- model-consistent boundary matching;
- unwind behavior when a boundary is reached;
- approximation error between matched points.

Compare static replication with dynamic delta hedging under the same costs and
market constraints.

## Numerical Methods

### Verification Discipline

Every numerical price should be accompanied by:

- a limiting or special-case check;
- convergence under finer resolution;
- uncertainty or error estimate;
- independent method comparison where feasible;
- vanilla repricing consistency after calibration.

### Barrier-Specific Issues

Barrier values can converge slowly in trees when nodes do not align with the
true barrier. Possible remedies include aligning nodes, interpolating between
inner and outer barriers, using adaptive meshes, and applying continuity
corrections for discrete monitoring.

The contract's monitoring convention is part of the payoff. Continuous and
daily monitoring are not interchangeable.

### American and Path-Dependent Claims

American-option Monte Carlo requires an exercise-policy approximation such as
regression. Report lower-bound bias and, where possible, an upper bound.
Path-dependent trees require a controlled approximation of the path state.

## Advanced Volatility Models and Model Risk

### Stochastic Volatility

Stochastic-volatility models add a volatility state process and can reproduce
smiles or skews through correlation and volatility-of-volatility. Heston is a
common tractable example. Assess whether the parameters are stable,
identifiable, and useful for the target payoff.

### SABR and Smile Dynamics

SABR can fit a maturity's smile and is useful for managing smile movement.
Its level, correlation, volatility-of-volatility, and elasticity parameters
control different aspects of the shape. Parameters commonly vary by maturity,
so cross-maturity consistency must be assessed rather than assumed.

### Rough Volatility

Rough-volatility models can fit observed volatility behavior and surfaces, but
simulation for exotics can be computationally demanding because future
increments depend on prior increments. Compare the claimed benefit with
simpler stochastic-volatility or lifted approximations.

### Local Volatility

Local volatility can exactly fit today's European vanilla prices after
smoothing. It therefore captures the risk-neutral marginal distribution at
each maturity. It does not necessarily capture the correct joint distribution
through time, so path-dependent exotics such as barriers may be materially
mispriced.

An exact vanilla fit is not proof of low model risk.

### Model-Risk Comparison

For an exotic, calibrate multiple plausible models to the same vanilla surface
and compare:

- exotic price;
- hedge ratios and hedge P&L;
- barrier-hit or path-event probabilities;
- stress behavior;
- parameter and calibration stability.

The dispersion is not a complete measure of model risk, but it is more
informative than reporting one calibrated number.

## Risk and Implementation Controls

- Use consistent market data and timestamps.
- Preserve the exact contract specification.
- Include transaction costs and liquidity.
- Separate pricing-measure calibration from physical-risk forecasting.
- Backtest hedges, not just prices.
- Report model, parameter, and numerical uncertainty.
- Stress spot, volatility level, skew, term structure, correlation, and jumps.
- Compare against simpler models and replication strategies.
- State where the model is expected to fail.

## Options-Reader Review Checklist

- Are contract terms and market inputs complete and consistent?
- Do parity and no-arbitrage bounds hold?
- Is the pricing method appropriate for exercise and path dependence?
- Are numerical convergence and error estimates reported?
- Are Greeks interpreted as local model sensitivities?
- Are hedges tested after costs and under discrete rebalancing?
- Does a learned hedge beat economic baselines out of sample?
- Is the surface arbitrage-controlled and stably interpolated?
- Are surface movement and minimum-variance delta assumptions tested?
- Does vanilla calibration identify the dynamics needed for the exotic?
- Are barrier and binary discontinuities handled explicitly?
- Are static and dynamic hedges compared fairly?
- Are multiple calibrated models used to expose model risk?
- Does added complexity improve price, hedge, or risk decisions?

## Source Map

- Chapters 10-20: option mechanics, trees, Black-Scholes-Merton, Greeks,
  hedging, and volatility surfaces.
- Chapter 19.14: machine learning for hedging.
- Chapters 21 and 27: numerical procedures and advanced models.
- Chapter 23: volatility and correlation estimation.
- Chapter 26: exotic options, volatility/variance swaps, and static
  replication.
- Chapter 27: stochastic, local, and rough volatility; path-dependent and
  barrier numerics; model-risk implications.

