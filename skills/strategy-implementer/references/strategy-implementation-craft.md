# Transcript-Distilled Strategy Implementation Craft

## Scope And Use

This reference distills the implementation-oriented practitioner corpus into
concrete coding discipline for the Coder agent. It is not investment advice and
not a claim that any transcript strategy is profitable; it converts recurring
*coding* practice into checks that keep a generated module faithful and
leakage-free. Use it as a craft checklist while writing `weights(...)`, not as
a source of trade ideas.

## The Universal Pipeline

Every strategy the corpus builds — moving-average crossovers, MACD, Bollinger
/ RSI mean reversion, cointegration pairs, intraday breakouts, cross-sectional
momentum — is the same five-stage pipeline:

1. **Universe** — which assets are eligible *at this date* (liquidity, price,
   listing filters applied point-in-time).
2. **Feature / signal** — a function of past prices/fundamentals.
3. **Target positions** — the signal mapped to weights under a construction
   rule.
4. **Schedule** — when positions update (rebalance frequency, holding period).
5. **Costs / holding** — turnover and frictions (usually applied by the bench,
   not the strategy).

Implement the stages in this order and the no-lookahead boundary falls out
naturally: each stage consumes only the output of earlier stages evaluated at
dates `<= as_of`.

## Indicator Construction Traps

These are the bugs that pass a naive eye but fail the no-lookahead test.

- **Whole-series smoothing then indexing.** Computing an EWM/rolling indicator
  over the entire price series once and reading it at `t` leaks the smoother's
  future-dependent state into time `t`. Construct the indicator from history
  `<= as_of` only. (The MACD walkthrough computes EMA-12, EMA-26, and the
  9-period signal line from the close column — correct only because each
  decision then uses the value *as known at that bar*, not a future-revised
  one.)
- **Warmup off-by-N.** A crossover needs the prior bar; an `n`-window needs `n`
  priors. Practitioners explicitly start the comparison loop *after* the
  zero/NaN warmup region ("I'm starting the loop at index two ... otherwise I'd
  get wrong signals"). In the contract, return `{}` until enough history
  exists rather than emitting a degenerate position.
- **Forward fill from the future.** Filling missing values with the next valid
  observation drags future information backward. Fill only from the past or
  treat as undefined.
- **Adjusted vs raw prices.** Mixing adjusted-close for the signal and raw
  open for execution (or vice versa) silently changes the result; pick one
  point-in-time field and stay consistent.

## Next-Bar Execution

The most repeated implementation lesson in the corpus: **a signal computed
from a bar's close cannot trade at that same close.** The Algovibes backtests
make it explicit — signals are based on close, "so we cannot assume that we
are buying the asset on this exact date ... but we can buy the asset on the
very next date," implemented as `real_buys = [i + 1 for i in buys]` and filling
at the next bar's open. Two consequences for generated code:

- Compute `weights(as_of)` from information at dates `<= as_of`; let the
  harness apply them to the forward return. Never read a price at `as_of` you
  could not have transacted at, and never peek one bar ahead to confirm a fill.
- Handle the boundary cases the corpus calls out: a closing signal with no
  matching open, a sell before any buy, a buy with no subsequent sell — return
  no position rather than fabricating a trade.

## Signal-To-Weight Recipes

- **Crossover (trend).** Long when fast crosses above slow, flat/short when it
  crosses below, using the prior bar's relation computed from past data.
- **Band mean-reversion (Bollinger / RSI / z-score).** Position proportional to
  standardized deviation from a trailing mean; cap gross exposure; revert
  toward neutral as the deviation closes.
- **Cross-sectional rank (momentum / value).** Rank the *currently eligible*
  universe at `as_of` on the trailing signal; long the top fraction, short the
  bottom; equalize leg magnitudes so the book nets ~zero.
- **Pairs / cointegration.** Trade the spread's standardized deviation; the
  hedge ratio must be estimated in `fit(data, train_end)` on data `<=
  train_end` and then *held fixed* out of sample — re-estimating it each bar on
  future data is leakage.

## Determinism And Warmup

- Seed any randomness from `params`; never from time, PID, or global state.
- No module-level mutable state that survives across `weights` calls.
- During warmup return `{}`. A non-empty book before the signal is defined is
  both a shape violation and an accidental always-on exposure.

## Expert Lenses

Use as implementation questions, not authority.

| Lens | Question for the implementer |
| --- | --- |
| Algovibes / QuantPy / Luke Finance | Is every indicator built from past data only, with warmup handled and execution pushed to the next bar? |
| QuantInsti (EPAT) | Does the code separate signal generation from execution, and is the point-in-time data contract respected end to end? |
| Ernest Chan | For mean-reversion/pairs, is the hedge ratio (and any parameter) estimated in-sample and frozen out-of-sample? Is the stationarity assumption stated? |
| Jim Simons / RenTec | Is the signal one modest, well-defined effect cleanly combined, rather than an over-engineered composite hiding a fit? |
| Victor Niederhoffer | What single observation (a shifted input, a held-out bar) would falsify this implementation's correctness? Where is the hidden tail exposure? |

## Guardrails

- Imports only from the sandbox allowlist; assume stdlib-only unless the
  numeric tier is enabled.
- Never read or infer a value at a date after `as_of`.
- Prefer the simplest faithful implementation; a verifiable loop beats an
  unverifiable vectorized trick.
- Implement the method, not the paper's claimed number.

## Provenance

Distilled from the implementation- and practitioner-oriented folders under
`Source_data/transcript/` (1,642 substantive Markdown transcripts across the
ten requested folders), especially the Python-coding sources
(`algovibes_notebooklm_transcripts`, `quantpy_notebooklm_transcripts`,
`quantinsti_notebooklm_transcripts`, `luke_finance_notebooklm_transcripts`)
and the execution/strategy-development sources
(`ernest_chan_playlist_notebooklm_transcripts`,
`algo_trading_with_kevin_davey_notebooklm_transcripts`,
`predicting_alpha_notebooklm_transcripts`), with research-philosophy lenses
from `jim_simons_playlist_notebooklm_transcripts`,
`victor_niederhoffer_playlist_notebooklm_transcripts`, and
`marcos_lopez_de_prado_playlist_notebooklm_transcripts`.
