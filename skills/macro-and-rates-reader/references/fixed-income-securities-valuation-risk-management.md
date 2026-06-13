# Fixed-Income Securities: Valuation, Risk Management, And Portfolio Strategies

Source: Lionel Martellini, Philippe Priaulet, and Stephane Priaulet,
*Fixed-Income Securities: Valuation, Risk Management and Portfolio
Strategies*.

## Why This Source Matters

This source links empirical yield-curve behavior, curve construction,
interest-rate models, credit-spread models, hedging, and active or passive bond
strategies. Use it to review whether a rates model is appropriate for the
instrument, horizon, and portfolio decision under study.

## Term-Structure Foundations

The zero-coupon, par, forward, swap, and credit-spread curves are distinct.
Curve construction requires choices about instruments, fitting method,
weights, smoothness, and pricing error. A curve that fits current prices well
need not describe future dynamics well.

Review:

- market instruments and filtering;
- bootstrapping or functional form;
- price-error weighting and liquidity;
- smoothness and local instability;
- extrapolation beyond liquid maturities;
- separation of Treasury, swap, and credit curves.

## Empirical Curve Behavior

Historical yield curves exhibit nonparallel movement, maturity-dependent
volatility, and strong common factors. PCA often identifies level, slope, and
curvature, but the source shows that factor importance and residual variance
vary across periods.

Do not turn "three factors explain most variance" into a timeless law.
Re-estimate factors across:

- countries and currencies;
- sampling frequencies;
- conventional, zero-bound, and negative-rate periods;
- tightening, easing, and inflation shocks;
- calm and stressed markets.

## Duration, Convexity, And Immunization

Duration hedging is exact only under restrictive assumptions, especially
small parallel curve shifts. Convexity and multifactor or key-rate exposures
matter for nonparallel changes. Immunization requires rebalancing as time,
rates, liabilities, and cash flows evolve.

Challenge:

- duration-only hedges;
- nominal immunization of inflation-linked liabilities;
- static hedges over long horizons;
- hedges built from historically stable factor loadings;
- omission of spread, basis, or optionality risk.

## Active Strategies And Scenario Analysis

Riding the yield curve, duration timing, and curve-shape trades earn returns
only under assumptions about future curve evolution, carry, roll-down, and
transaction costs. Scenario analysis is useful but difficult: scenarios must
be realistic, internally coherent, and broad enough to expose nonlinear loss.

Ask whether a strategy's return is:

- forecast alpha;
- term or credit premium;
- carry and roll-down;
- convexity or volatility exposure;
- compensation for liquidity or tail risk.

## Term-Structure Models

The source covers short-rate and forward-rate models, including Vasicek, CIR,
multifactor affine models, Ho-Lee, Hull-White, and HJM.

Model choice determines:

- whether rates can become negative;
- mean reversion;
- volatility shape;
- number of risk factors;
- fit to today's curve;
- tractability and derivative pricing.

Separate physical-dynamics questions from risk-neutral pricing questions.
A model calibrated for derivative pricing is not automatically a valid
forecasting or policy-reaction model.

## Credit Spreads

Credit spread reflects default probability, recovery, liquidity, risk premium,
and sometimes option effects. A spread model should not attribute all movement
to expected default. Rate and spread dynamics can interact and change sign
across cycles.

## Reviewer Diagnostics

- Is the model selected for fit, forecasting, hedging, or pricing, and is that
  objective explicit?
- Are physical and risk-neutral parameters confused?
- Are factor loadings and mean-reversion estimates stable across cycles?
- Is curve fit evaluated separately from dynamic performance?
- Does scenario analysis include changes in volatility, correlation, spreads,
  and liquidity?
- Do active-strategy returns survive transaction costs and alternative curve
  paths?

## Reviewer Use

Use this source for term-structure models, curve fitting, PCA, immunization,
active rates strategies, derivatives, and credit spreads. Require model choice
to follow the economic question rather than mathematical convenience.

## Source Map

- Chapters 3-4: curve behavior, theories, PCA, and curve construction
- Chapters 5-9: duration, multifactor hedging, portfolio strategies, and
  performance
- Chapter 12: yield-curve dynamics and term-structure models
- Chapter 13 onward: credit spreads and fixed-income derivatives

