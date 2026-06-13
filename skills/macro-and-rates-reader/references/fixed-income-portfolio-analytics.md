# Fixed-Income Portfolio Analytics

Source: David Jamieson Bolder, *Fixed-Income Portfolio Analytics: A Practical
Guide to Implementing, Monitoring and Understanding Fixed-Income Portfolios*.

## Why This Source Matters

Bolder organizes fixed-income portfolio analysis around risk factors rather
than security labels. It connects curve fitting, factor exposures, return
attribution, covariance estimation, scenario analysis, and active risk. Use it
to review whether a rates paper translates a forecast or model into a
portfolio-level exposure whose risk changes with the market regime.

## Portfolio-Analytics Frame

The core dimensions are:

- exposure: sensitivity to underlying risk factors;
- risk: exposure combined with factor volatility and dependence;
- return: realized contribution from each factor;
- benchmark-relative positioning and performance attribution.

Asset classes are not risk factors. Different instruments can share curve,
spread, currency, volatility, or liquidity exposures. Conversely, one
security can embed several factors. Review portfolio claims at the risk-factor
level.

## Curve Exposure

Modified duration summarizes sensitivity to a parallel yield shift, but a
portfolio can have the same total duration while carrying very different
positions across tenors. Key-rate durations and curve-sector exposures reveal
level, slope, and curvature bets that aggregate duration conceals.

Require:

- the curve and instruments used to compute sensitivities;
- key-rate bump construction and interpolation;
- separation of rates, spread, currency, carry, roll, and convexity;
- exposure relative to a relevant benchmark;
- revaluation for large or nonlinear shocks.

## Curve Models And PCA

Yield changes are highly correlated across nearby maturities. PCA compresses
the covariance structure into statistically orthogonal factors commonly
interpreted as level, slope, and curvature. These interpretations are useful,
but loadings and variance shares depend on market, sample, frequency, and
period.

Do not assume that three historical factors remain sufficient. The source
shows that explained variance and factor dominance vary by year, with
non-negligible residuals in some periods.

Review:

- estimation window and data frequency;
- standardization and curve-tenor grid;
- loading stability and sign conventions;
- out-of-sample residual risk;
- whether economic labels are imposed after observing statistical factors;
- behavior during policy transitions and market stress.

## Dynamic Risk

An exposure snapshot is not a risk estimate. The same duration position can
carry different risk as volatility and correlations change. Portfolio risk
depends heavily on the estimated covariance matrix.

The book explores:

- daily versus monthly estimation;
- sample length and weighting schemes;
- historical and exponentially weighted estimates;
- simulated factor outcomes;
- sensitivity to correlation assumptions;
- stress tests including perfect correlation.

The practical lesson is that covariance is estimated, unstable, and often most
dangerous when diversification assumptions fail.

## Return Attribution

Decompose active return into curve, spread, currency, carry, roll-down,
convexity, and residual components where relevant. Attribution should agree
with actual portfolio positions and reveal whether realized profits came from
the intended macro thesis or from an unacknowledged exposure.

Ask:

- Does ex-ante risk attribution reconcile with ex-post return attribution?
- Is unexplained residual material or persistent?
- Did a supposed duration view actually profit from curve shape, carry, or
  spread compression?
- Are benchmark choices driving the result?

## Reviewer Diagnostics

- Are rate changes treated as independent or identically distributed despite
  evidence of changing volatility, correlation, and persistence?
- Does the factor model survive different windows and rate cycles?
- Are correlations stressed upward rather than accepted from normal periods?
- Are filtered or smoothed returns introducing apparent predictability?
- Are risk estimates robust to daily versus monthly observations?
- Is a portfolio strategy evaluated relative to its mandate and benchmark?

## Reviewer Use

Use this source for portfolio-level rate strategies, factor models, PCA,
tracking error, and attribution. Demand a bridge from forecast to exposure,
from exposure to dynamic risk, and from risk to realized return.

## Source Map

- Part I: risk factors, sensitivities, duration, and convexity
- Part II: fitting and modeling yield curves, including PCA
- Return decomposition and performance attribution
- Portfolio risk, covariance estimation, simulation, and stress testing

