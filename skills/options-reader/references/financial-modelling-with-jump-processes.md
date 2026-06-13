# Financial Modelling with Jump Processes: Options-Reader Distillation

Source: Rama Cont and Peter Tankov, *Financial Modelling with Jump Processes*.

## Contents

- [Why this source matters](#why-this-source-matters)
- [Core modeling stance](#core-modeling-stance)
- [Empirical and market evidence](#empirical-and-market-evidence)
- [Jump-model taxonomy](#jump-model-taxonomy)
- [Pricing in incomplete markets](#pricing-in-incomplete-markets)
- [Hedging implications](#hedging-implications)
- [Vanilla calibration](#vanilla-calibration)
- [Volatility-surface implications](#volatility-surface-implications)
- [Exotic pricing and numerical methods](#exotic-pricing-and-numerical-methods)
- [Model-selection diagnostics](#model-selection-diagnostics)
- [Options-reader review checklist](#options-reader-review-checklist)
- [Source map](#source-map)

## Why This Source Matters

This book is the specialist reference for deciding whether discontinuous price
dynamics materially change an option-pricing or hedging conclusion. It connects
four questions that papers often separate:

1. What statistical features of returns motivate jumps?
2. What risk-neutral jump dynamics are implied by option prices?
3. What becomes unhedgeable when jumps are admitted?
4. Is calibration stable enough to support pricing and risk decisions?

The book's central warning is that adding even small jump risk destroys market
completeness. Once that happens, a unique arbitrage price and perfect
underlying-only replication generally disappear. Pricing, calibration, and
hedging choices must therefore be evaluated together.

## Core Modeling Stance

### Separate Statistical and Risk-Neutral Dynamics

Do not assume that a model fitted to historical returns is automatically an
option-pricing model. Historical estimation concerns the physical probability
measure. Pricing requires a martingale measure, and jump models admit many
equivalent martingale measures.

When reading a paper, identify:

- the physical dynamics, if any;
- the risk-neutral dynamics;
- the rule used to move between them;
- which jump parameters or risks change under that rule;
- whether the rule is economically defended or merely convenient.

### Treat Completeness as an Assumption, Not a Fact

Diffusion models with one traded risky asset and one Brownian risk source can
produce complete markets. Jump models generally do not. A paper that inserts a
jump term but continues to speak as if every claim is exactly replicable has
not resolved the central consequence of its own model.

### Distinguish Fit from Dynamics

A model can fit today's vanilla surface yet imply poor future smile dynamics,
unstable hedges, or implausible paths. Cross-sectional fit is evidence about one
slice of risk-neutral marginals, not proof that the model captures the joint
distribution through time.

## Empirical and Market Evidence

### Why Move Beyond Brownian Motion

The book motivates jumps through features that simple continuous diffusions do
not represent naturally:

- large price moves over short intervals;
- heavy-tailed return distributions;
- asymmetry between downward and upward moves;
- changes in return behavior across sampling frequencies;
- short-maturity implied-volatility skews and smiles;
- residual risk in supposedly delta-hedged positions.

The relevant question is not whether a diffusion can be made flexible enough
to mimic one of these facts. It is whether the proposed mechanism explains all
facts needed for the task without forcing implausible parameters elsewhere.

### Short-Maturity Options Are Especially Diagnostic

Jump risk has a strong effect on short-dated out-of-the-money options because a
large discontinuous move can make them relevant immediately. Diffusion-based
stochastic-volatility models may need extreme volatility-of-volatility values
to reproduce pronounced short-term skews. Jump models can generate such skews
directly through the distribution and asymmetry of jump sizes.

For equity options, a steep downside skew is consistent with risk-neutral fear
of large negative jumps. Do not confuse this risk-neutral interpretation with a
historical estimate of crash frequency.

## Jump-Model Taxonomy

### Finite-Activity Jump Diffusions

These combine Brownian diffusion with a finite number of jumps over finite
time. Common examples include Merton's normally distributed jumps and Kou's
double-exponential jumps.

Use them when:

- interpretability and tractability matter;
- a distinct jump-event mechanism is plausible;
- closed-form or rapidly convergent European-option pricing is valuable.

Challenge them on:

- whether finite jump intensity is empirically adequate;
- sensitivity of calibration to jump intensity and jump-size parameters;
- whether the diffusion and jump components are separately identifiable.

### Infinite-Activity Levy Models

These permit infinitely many small jumps in finite time. Examples discussed in
the book include tempered-stable, generalized-hyperbolic, variance-gamma, and
subordinated Brownian-motion constructions.

Use them when:

- small-jump activity and heavy tails are central;
- characteristic-function methods are useful;
- the model needs richer distributional shape than a finite jump diffusion.

Challenge them on:

- path variation and small-jump behavior;
- parameter identifiability;
- consistency between historical and risk-neutral measures;
- simulation approximations for small jumps.

### Time-Inhomogeneous and Stochastic-Volatility Jump Models

Stationary Levy increments can be too restrictive for an evolving volatility
surface. Additive processes relax time homogeneity. Models such as Bates add
jumps to stochastic volatility. Time-changed Levy processes and
Ornstein-Uhlenbeck volatility models add further flexibility.

More flexibility is not automatically better. Require evidence that the added
state variables or time dependence improve out-of-sample prices, hedges, or
risk forecasts rather than only in-sample surface fit.

## Pricing in Incomplete Markets

### No Unique Arbitrage Price

In an incomplete market, absence of arbitrage gives a range of possible prices,
not one unique price. A paper must specify its pricing rule. Candidate rules in
the book include:

- Merton's assumption that jump risk earns no premium;
- superhedging;
- utility-indifference pricing;
- mean-variance or quadratic hedging;
- selection of an "optimal" martingale measure, such as minimal entropy.

Each rule embeds a different economic or risk criterion.

### Merton's Approach

Merton changes the Brownian drift while leaving the jump-time and jump-size
distribution unchanged under the pricing measure. The resulting hedge offsets
the diffusion component but leaves jump exposure. This is defensible only when
jump risk can reasonably be treated as diversifiable.

For index options, that defense is weak: index jumps can represent correlated,
systemic moves. A reviewer should flag any use of Merton's pricing rule that
does not discuss the residual jump-risk premium.

### Superhedging

Superhedging seeks a strategy whose terminal value covers the claim in all
admissible scenarios. It is preference-free but often produces very wide price
bounds and economically unhelpful buy-and-hold solutions in jump models.

Do not present a superhedging bound as a practical fair value without assessing
its width and capital cost.

### Utility and Quadratic Criteria

Utility-indifference pricing makes preferences and initial wealth relevant.
Quadratic hedging minimizes expected squared hedging error and is often more
tractable. Both approaches make explicit what perfect replication conceals:
hedging is an optimization problem over residual risk.

When a paper calls a hedge "optimal," identify the loss function, probability
measure, admissible strategies, and instruments. Optimality is criterion-specific.

## Hedging Implications

### Residual Risk Is Structural

With jumps, continuous delta hedging does not eliminate risk. A jump moves the
underlying across a finite interval before the hedge can be adjusted. The
option-value change across that interval is nonlinear and cannot generally be
matched by the pre-jump delta.

Require papers to report the residual hedging-error distribution, not just mean
P&L or average error.

### Options Are Genuine Hedging Instruments

In complete diffusion models, options are theoretically redundant. In jump
models, liquid vanilla options can reduce residual jump risk and become useful
instruments for static or quasi-static hedging of exotics.

Assess whether the proposed hedge:

- uses only the underlying or also liquid vanillas;
- minimizes local, terminal, or tail loss;
- accounts for vanilla bid-ask spreads and liquidity;
- remains valid when the calibrated surface moves.

### Replication and Hedging Are Different

Use "replication" only for an exact payoff match under stated assumptions.
Use "hedging" for risk reduction with a residual error. A paper that reports
one path or one simulated average as proof of replication is overstating its
result.

## Vanilla Calibration

### Calibration Is an Ill-Posed Inverse Problem

Observed option prices do not necessarily identify a unique jump distribution.
There may be no exact solution, many nearly equivalent solutions, flat
directions in the loss landscape, or discontinuous parameter responses to
small input changes.

The number of parameters alone does not determine calibration stability.
Convexity, conditioning, parameterization, and data quality matter more.

### Weight by Market Reliability

Calibration errors should reflect liquidity and quote uncertainty. If bid-ask
spreads are available, use them. Because option-price errors are not comparable
across strikes and maturities, implied-volatility errors or price errors scaled
by Black-Scholes vega are often more meaningful than unweighted price errors.

Require the paper to state:

- quote filters and timestamp alignment;
- bid, ask, mid, or last-trade use;
- objective function and weights;
- no-arbitrage cleaning or smoothing;
- optimizer, starts, bounds, and convergence checks.

### Regularize and Test Stability

The book presents relative entropy against a prior as a way to stabilize
calibration. The broader lesson is to prefer a slightly worse fit inside market
error bounds when it produces a materially more stable and economically
coherent model.

Test calibration under:

- small quote perturbations;
- multiple initial parameter guesses;
- alternative strike and maturity subsets;
- adjacent days;
- alternative weights and regularization strengths.

Report parameter dispersion, surface error, and downstream price and hedge
dispersion.

## Volatility-Surface Implications

### Cross-Sectional Shape

Jump asymmetry can produce skew; symmetric jump distributions can produce
smiles. Jump activity is especially visible in short maturities. Stochastic
volatility can improve longer-horizon dynamics and persistence.

Do not conclude that a jump model is structurally correct merely because it
fits the current surface. Compare:

- short- versus long-maturity errors;
- downside versus upside-wing errors;
- fit in price, implied volatility, and vega-scaled units;
- stability of forward smiles;
- surface dynamics after spot moves.

### Static Fit Versus Dynamic Consistency

Repeated daily calibration may produce large parameter changes even when the
surface moves modestly. Treat this as evidence of weak identification or poor
dynamic specification. Using the prior day's calibrated measure as a prior can
enforce continuity, but the remaining instability must still be reported.

## Exotic Pricing and Numerical Methods

The book develops several implementation routes:

- characteristic-function and Fourier methods for European claims;
- partial integro-differential equations for European, barrier, and American
  options;
- multinomial trees and Markov-chain approximations;
- finite differences, method of lines, and Galerkin methods;
- Monte Carlo simulation, including approximations for infinite activity.

Method choice must match payoff structure. For barriers and other
path-dependent claims, inspect nonlocal jump terms, boundary treatment,
monitoring conventions, truncation of the jump domain, and convergence.

For any exotic result, require:

- convergence across grid, time-step, path-count, and truncation choices;
- comparison with an analytic or simpler limiting case;
- calibration-consistent vanilla repricing;
- sensitivity to jump tails and surface perturbations;
- a hedge-error study under plausible model misspecification.

## Model-Selection Diagnostics

Use the following hierarchy:

1. **Purpose:** pricing, surface interpolation, hedging, scenario generation,
   or risk measurement?
2. **Observable targets:** which quotes, returns, or hedge outcomes identify
   the model?
3. **Mechanism:** which feature requires jumps rather than a flexible
   diffusion?
4. **Completeness:** what risk remains unhedgeable?
5. **Calibration:** is the inverse problem stable inside market noise?
6. **Dynamics:** does the model produce plausible smile and hedge behavior?
7. **Numerics:** are jump integrals and path features resolved accurately?
8. **Decision value:** does added complexity improve the relevant outcome?

## Options-Reader Review Checklist

- Does the paper distinguish physical and risk-neutral jump dynamics?
- Is the selected martingale measure or pricing criterion explicit?
- Are residual jump risks acknowledged and measured?
- Are jump intensity and jump-size distribution separately identified?
- Does the model improve short-dated wings without implausible parameters?
- Are vanilla quotes cleaned, synchronized, and weighted by reliability?
- Is calibration tested for multiple starts and quote perturbations?
- Is regularization disclosed and sensitivity-tested?
- Are surface fit and surface dynamics evaluated separately?
- Does the exotic depend on joint path dynamics not identified by vanillas?
- Are numerical convergence and boundary treatments documented?
- Are hedges evaluated under jumps, costs, discrete trading, and liquidity?
- Does the proposed complexity improve out-of-sample pricing or hedging?

## Source Map

- Chapter 1: empirical motivation, implied smiles and skews, hedging and risk.
- Chapters 3-5: Levy processes, jump-model construction, multidimensional
  dependence.
- Chapters 6-7: simulation, estimation, empirical properties, and pitfalls.
- Chapters 8-10: stochastic calculus, martingale measures, incomplete-market
  pricing, and hedging.
- Chapters 11-12: risk-neutral exponential-Levy pricing and numerical methods.
- Chapter 13: calibration as an inverse problem, weighting, and regularization.
- Chapters 14-15: time-inhomogeneous and stochastic-volatility jump models.

