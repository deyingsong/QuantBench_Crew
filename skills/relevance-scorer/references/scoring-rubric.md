# Scout Research-Value Rubric

## Contents

- Purpose
- Dimensions and weights
- Penalties
- Confidence
- Reading depth
- Decision bands
- Required output

## Purpose

Rank papers by expected value of further analysis:

`expected research value = decision relevance x probability of learning x feasibility / downstream cost`

The deterministic implementation uses disclosed metadata as a first-pass proxy. Full-text review may reverse the ranking.

## Dimensions And Weights

### Charter Fit: 35%

Ask whether the paper directly tests the crew's research purpose, themes, must-haves, and exclusions. A fashionable off-charter paper should not outrank an on-charter paper.

### Empirical Evidence: 20%

Reward:

- explicit out-of-sample, walk-forward, or genuinely untouched evaluation;
- robustness, sensitivity, subsample, placebo, or replication tests;
- comparisons with sensible baselines;
- falsifiable numerical claims.

Do not treat a holdout as protection from repeated researcher iteration unless trial counts and process are disclosed.

### Implementability: 20%

Reward:

- released code;
- named and accessible data;
- explicit universe, feature timing, portfolio construction, rebalance, holding period, and parameters;
- a method that can be independently reconstructed.

Distinguish public, vendor, proprietary, and unknown data. Unknown is not public.

### Economic Relevance: 15%

Reward:

- results net of transaction costs and slippage;
- turnover, liquidity, market impact, and capacity discussion;
- drawdown, tail risk, and portfolio-level consequences;
- a plausible mechanism and identifiable counterparty.

### Information Gain: 10%

Reward work likely to change a belief or decision:

- a genuinely new dataset, setting, or method;
- a credible challenge or replication of prior evidence;
- an explanation of when or why a known effect works or fails.

Do not reward novelty language by itself.

## Penalties

Apply explicit penalties for:

- strategy claims that omit costs;
- proprietary or inaccessible data;
- in-sample evidence without disclosed out-of-sample testing;
- sparse metadata that prevents meaningful assessment;
- hidden multiple testing, data snooping, look-ahead, survivorship, or selection bias;
- unnecessary complexity without incremental baseline value.

Penalties are warnings at Scout stage, not final verdicts.

## Confidence

Score confidence separately from research value. Raise confidence for complete abstracts, authors, URLs, dates, and concrete claims. Low confidence means "inspect before trusting," not automatically "irrelevant."

## Reading Depth

Use a staged funnel:

1. Survey: title, keywords, abstract, conclusion. Stop freely.
2. Validate promise: figures, tables, captions, headline claims, baselines.
3. Reconstruct only promoted work: methods, data, code, exact experimental design.

The queue should contain many survey-level records and few reconstruction-level commitments.

## Decision Bands

- `0.75-1.00`: promote unless a hard exclusion applies.
- `0.55-0.74`: queue for targeted second-pass validation.
- `0.35-0.54`: defer unless it fills a known gap.
- `0.00-0.34`: reject with a short reason.

Use bands as defaults, not substitutes for judgment.

## Required Output

Return:

- total score in `[0,1]`;
- dimension scores;
- disclosed positive signals;
- explicit penalties;
- confidence;
- concise rationale;
- one recommended next action.
