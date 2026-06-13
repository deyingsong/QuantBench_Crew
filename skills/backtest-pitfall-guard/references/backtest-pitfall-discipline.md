# Transcript-Distilled Backtest Pitfall Discipline

## Scope And Use

This reference distills the corpus's most consistent warning — that backtests
systematically overstate future performance — into code-generation-time
defenses. It is not investment advice. Use it to decide whether a generated
candidate is *faithful*, not whether it is profitable.

## Why Backtests Lie

Lopez de Prado's framing: a backtest is a historical simulation whose
performance can come from signal or from noise; because competition drives the
signal-to-noise ratio very low, an impressive result is more likely overfit
than real. Two forces compound:

- **Multiple testing.** Run enough variations and one will look great by
  chance — like rolling ten dice millions of times until all show six, then
  showing only that roll. The result looks like signal because the trial count
  is concealed.
- **Selection bias.** Reporting only the best-of-many trials produces a
  winner's curse: what looked best in-sample tends to underperform out of
  sample. Selection bias plus overfitting is the worst case, and it is the
  default behavior of an unconstrained generate-and-keep-the-best loop.

The defense is **transparency about trials** plus **code that is structurally
hard to overfit**.

## Leakage Taxonomy

Leakage is future information reaching a past decision. Catch each form in
generated code:

- **Temporal look-ahead** — reading a price, feature, or label dated after the
  decision time; trading on a bar's close using that same close.
- **Parameter leakage** — fitting means, vols, scalers, hedge ratios, or model
  coefficients on data that includes the test period; re-estimating each bar
  on future data. Estimate in `fit(data, train_end)` on `<= train_end`, then
  freeze.
- **Label leakage** — overlapping or forward-looking labels that bleed the
  target into the features.
- **Preprocessing leakage** — normalizing, ranking, or imputing using
  full-sample statistics instead of point-in-time ones.
- **Survivorship / point-in-time** — selecting the universe by who survived to
  the sample end, or using restated fundamentals not available at the time.

## The Over-Optimization Funnel

Kevin Davey's "5 big mistakes" names the trap precisely: traditional
optimization produces a beautiful in-sample backtest that fails forward.
Crucially, **out-of-sample and walk-forward testing can be exploited too** —
"every time you do a little improvement, your out-of-sample isn't quite
out-of-sample anymore ... 90%, then 80%, then 50%, pretty soon it's in-sample."
Implications for the generate-test-fix loop:

- Each iteration that edits code in response to an out-of-sample score spends
  out-of-sample information. Bounded iterations and a never-seen embargoed
  segment are the protection, not the walk-forward label.
- Prefer coarse, spec-driven parameter choices over fine-grained search; a
  parameter "tuned" to a precise value is usually fitting noise.
- Define acceptance criteria *before* iterating, so the loop is not a search
  for the interpretation that maximizes the score.

## Holdout Does Not Cure Overfitting

A frequent misunderstanding (Lopez de Prado): splitting into train/test helps
for some purposes but does **not** prevent overfitting, because it does not
control the number of trials. Worse, with **memory effects** (serial
correlation, mean reversion), overfitting actively backfires — bets get
contradicted by future outcomes. So: do not treat a clean holdout as a
validity certificate, and keep a research log (here, the run manifest) of every
trial, including discarded ones.

## Trial Accounting

The manifest records every candidate's score — discarded trials included —
because uncounted trials are how selection bias creeps in. When guarding a
candidate, confirm:

- all generation attempts and scores are recorded, not just the winner;
- the count of attempts that produced the accepted candidate is visible;
- nothing improved the score by hiding a trial, dropping an asset, or peeking.

## Expert Lenses

Use as red-team questions, not authority.

| Lens | Question for the guard |
| --- | --- |
| Marcos Lopez de Prado | How many candidates were tried, how correlated are they, and is the accepted one's score deflated for the trial count? Are there memory effects that make overfitting actively harmful? |
| Kevin Davey | Did the generate-test-fix loop quietly convert out-of-sample into in-sample by iterating on OOS feedback? Were acceptance hurdles set up front? |
| Ernest Chan | Are estimated parameters frozen out-of-sample? Does the result lean on a few illiquid names or a fragile stationarity assumption? |
| Predicting Alpha | Is the edge specified before the data is touched, or discovered by searching combinations until one works? |
| Jim Simons / RenTec | Is this one modest, independently justified effect, or an over-engineered composite that fit the sample? |
| Victor Niederhoffer | Which single held-out bar or shifted input would falsify the result? Where is the unmodeled tail? |

## Guardrails

- A passing sandbox/template test proves mechanical correctness, not validity.
- Never raise a score by concealing trials, dropping assets, peeking ahead, or
  refitting on the future.
- Treat a convenient spec interpretation that matches the headline number as a
  warning sign, not a confirmation.
- Do not issue investment advice.

## Provenance

Distilled from the ten requested folders under `Source_data/transcript/`
(1,642 substantive Markdown transcripts), especially
`marcos_lopez_de_prado_playlist_notebooklm_transcripts` (backtest overfitting,
selection bias, multiple testing, deflated Sharpe, memory effects),
`algo_trading_with_kevin_davey_notebooklm_transcripts` (the over-optimization
and walk-forward-contamination funnel, acceptance hurdles, when to quit),
`ernest_chan_playlist_notebooklm_transcripts` (frozen parameters, statistical
significance of backtests, pitfalls of backtesting),
`predicting_alpha_notebooklm_transcripts` and
`quantinsti_notebooklm_transcripts` (specify the edge first, realistic
execution), with research-philosophy lenses from
`jim_simons_playlist_notebooklm_transcripts` and
`victor_niederhoffer_playlist_notebooklm_transcripts`.
