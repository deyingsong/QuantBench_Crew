# High-Frequency Financial Econometrics

Source: Yacine Ait-Sahalia and Jean Jacod, *High-Frequency Financial
Econometrics*.

## Why This Source Matters

This source gives the rigorous statistical foundation for learning from
high-frequency prices observed discretely, irregularly, and with market
microstructure noise. Use it when a paper estimates volatility, covariation,
jumps, or jump activity from intraday data. Its central warning is that more
observations do not automatically mean more information.

## Observation Versus Latent Process

The economically meaningful price process is not directly observed. Recorded
quotes and trades are affected by:

- bid-ask bounce and discreteness;
- rounding and price grids;
- data errors;
- random and potentially endogenous sampling times;
- market rules that create apparent jumps;
- asynchronous observations across assets.

At very high sampling frequencies, measured returns can be dominated by
microstructure noise rather than efficient-price variation.

## Sampling Diagnostics

State precisely:

- whether observations are trades, quotes, midpoints, or constructed prices;
- whether sampling is calendar-time, tick-time, business-time, or refresh-time;
- how duplicate, crossed, locked, stale, or erroneous observations are treated;
- whether sampling times depend on volatility or price moves;
- how multiple assets are synchronized;
- whether auctions and overnight changes are included.

Downsampling can reduce noise but discards information. Noise-robust methods
such as subsampling, two-scale estimators, pre-averaging, realized kernels, and
multi-scale estimators each impose their own tuning and asymptotic conditions.

## Volatility And Covariation

Realized volatility is simple only under a continuous process, clean
observations, and suitable sampling. With jumps, standard realized variation
mixes continuous variation and jump variation. With noise, naive realized
volatility can diverge as frequency increases.

Review:

- whether the estimator is robust to both jumps and noise;
- finite-sample behavior, not only asymptotic consistency;
- sensitivity to tuning thresholds and sampling frequency;
- intraday seasonality and state dependence;
- confidence intervals and feasible standard errors;
- covariance bias from asynchronicity.

## Jump Diagnostics

A large recorded return is not automatically a jump in the latent price
process. Market rules, bad prints, bouncebacks, rounding, and clustered moves
can produce false detections. Conversely, noise can obscure true jumps.

Require:

- a declared null hypothesis: no jumps, presence of jumps, finite activity, or
  infinite activity;
- noise-robust testing where relevant;
- sensitivity to truncation thresholds;
- treatment of clustered and common jumps;
- distinction between price jumps and volatility jumps;
- awareness of the finite-sample "peso problem": a jump-capable process may
  exhibit no jump in the observed window.

## Reviewer Use

Use this source to challenge any claim based on tick-level volatility or jump
statistics. Trace the conclusion through three layers:

1. latent-process assumption;
2. observation and sampling scheme;
3. estimator and finite-sample implementation.

A theorem under exogenous observation times and a particular noise model does
not validate an empirical result when trade intensity is endogenous or the
feed contains exchange-specific artifacts.

## Source Map

- Chapter 2: market data, sampling, noise, and mitigation
- Chapters 3-9: high-frequency asymptotics and volatility estimation
- Chapters 10-14: jump detection, jump activity, and co-jumps
- Appendices: limit theory and estimator assumptions

