# Building Winning Algorithmic Trading Systems

Source: Kevin J. Davey, *Building Winning Algorithmic Trading Systems*.

## Why This Source Matters

Davey provides a practical strategy-development process centered on resisting
overfitting, charging trading costs, testing out of sample, and observing a
strategy before live deployment. The examples are not HFT-specific and some
cost heuristics are too coarse for microstructure research. Use the process
discipline, not the fill assumptions.

## Development Guardrails

The recommended progression is broadly:

1. define objectives and development rules before seeing results;
2. perform initial historical testing;
3. use out-of-sample or walk-forward testing;
4. assess uncertainty with Monte Carlo methods;
5. incubate the strategy before committing capital;
6. compare live behavior with expectations.

The key behavioral warning is that researchers can surreptitiously optimize
the test design itself by repeatedly changing windows, parameters, or
acceptance rules.

## Costs And Slippage

The book strongly rejects backtests with zero commissions or slippage. That
principle is essential. However, simple fixed-tick assumptions, including zero
slippage for limit orders, are not adequate for HFT or LOB research.

Replace coarse slippage rules with:

- queue-aware fill probabilities;
- adverse-selection markouts;
- partial fills and missed trades;
- maker/taker fees and rebates;
- latency and cancel failure;
- state-dependent spread and impact;
- contract and venue-specific costs.

## Walk-Forward Testing

Walk-forward testing aggregates sequential out-of-sample periods and more
closely resembles repeated production decisions. It remains vulnerable if the
researcher chooses the windows or fitness function after inspecting the
results.

For HFT, walk forward across:

- calendar periods and volatility regimes;
- tick-size and fee-rule changes;
- instruments and venues;
- hardware or feed changes;
- opening, continuous, closing, and stress sessions.

## Monte Carlo And Incubation

Simple trade reshuffling assumes exchangeable trade outcomes and can fail when
returns are serially dependent or regime clustered. Preserve dependence with
block or state-aware resampling where appropriate.

Incubation is a useful paper-trading or shadow-production stage, but it only
tests execution if it records realistic queue position, acknowledgments,
latency, and missed fills.

## Reviewer Diagnostics

- Was the research protocol specified before final evaluation?
- How many strategy variants were attempted?
- Are costs and fills credible for the order types used?
- Does uncertainty analysis preserve dependence and regime clustering?
- Is out-of-sample performance truly untouched?
- Do shadow and live results reconcile with the backtest?

## Reviewer Use

Use this source as a procedural skepticism checklist. It is especially valuable
when a microstructure paper reports an attractive strategy result but gives
little information about the research search space or the path from backtest
to live execution.

## Source Map

- Performance-report and cost review
- Out-of-sample and walk-forward analysis
- Monte Carlo uncertainty analysis
- Incubation and transition to live trading

