# Transcript-Distilled Strategy Evaluation Discipline

## Core Process

The requested practitioner and investor corpus repeatedly distinguishes a
research result from a deployable strategy. Use a staged evaluation funnel:

1. Define objectives, constraints, and acceptance rules before testing.
2. Run preliminary tests on limited development data.
3. Freeze the method and evaluate with rolling or walk-forward out-of-sample
   tests.
4. Compare against simple, economically meaningful baselines and random nulls.
5. Add realistic costs, slippage, latency, liquidity, and sizing assumptions
   from the beginning.
6. Run Monte Carlo, stress, and scenario checks.
7. Incubate with paper or small-live trading before scaling.
8. Monitor live degradation against the frozen expectation.

Kevin Davey's material emphasizes that attractive optimized backtests often
degrade in real time; walk-forward tests are intentionally harder and more
informative. QuantInsti and Ernest Chan repeatedly stress data timing,
out-of-sample evaluation, market-regime changes, and execution realism.
Lopez de Prado emphasizes that holdouts alone do not correct undisclosed
multiple testing.

## Dataset Suite

Evaluate across datasets with declared purposes:

- `signal world`: the strategy should detect a known or planted effect;
- `null world`: the strategy should not manufacture an edge from noise;
- `alternate sample`: test another period, market, universe, or provider;
- `adverse regime`: test crises, illiquidity, volatility, or structural change;
- `real-world data`: validate after synthetic tests establish harness behavior.

Declare `expect_edge` before seeing results. Correctly rejecting noise is as
important as finding a planted effect.

## Baselines And Metrics

Use baselines that answer different questions:

- buy-and-hold or equal-weight: does complexity improve a cheap alternative?
- simple factor or rule: is novelty only repackaging?
- random matched-turnover: is performance distinguishable from luck after
  comparable trading costs?
- paper claim: does the reproduction land within a declared tolerance?

Assess return alongside volatility, drawdown, downside/tail risk, turnover,
capacity, correlation, factor exposure, and portfolio contribution. Markowitz,
Sharpe, Bogle, Asness, Dalio, and Thorp material reinforces that isolated
return is not the decision variable: risk, correlation, cost, leverage, and
survival determine usefulness.

## Expert Lenses

- Lopez de Prado: disclose trial counts, selection, dependence, and deflated
  performance.
- Ernest Chan: aggregate relevant data, reduce needless predictors, preserve
  out-of-sample validity, and test execution assumptions.
- Kevin Davey / QuantInsti / Predicting Alpha: require a repeatable funnel from
  idea through backtest, walk-forward, Monte Carlo, incubation, and live.
- Thorp: evaluate expected value, sizing, leverage, and ruin.
- Markowitz / Sharpe / Bogle / Asness: judge incremental portfolio value versus
  diversified, low-cost, and factor-aware baselines.
- Dalio / Druckenmiller / Tudor Jones / Fink: ask how regime, liquidity,
  policy, and capital flows alter the result.
- Simons / Shaw / Griffin / Cohen / Englander: value repeatable research,
  independent signals, high-quality data, disciplined experimentation, and
  institutional controls.

Use these as questions, not authority bonuses.

## Provenance

Distilled from all 27 requested folders under `Source_data/transcript/`
(1,762 substantive Markdown transcripts), especially the Predicting Alpha,
QuantInsti, Luke Finance, Kevin Davey, Lopez de Prado, Ernest Chan, Asness,
Dalio, Thorp, Markowitz, Sharpe, Simons, Shaw, Griffin, and Englander material.
