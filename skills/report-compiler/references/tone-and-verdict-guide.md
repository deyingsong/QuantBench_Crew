# Tone And Verdict Guide

## Voice

Write like an internal research committee:

- direct
- quantified
- calm
- skeptical without being theatrical
- explicit about uncertainty

Prefer "net Sharpe 0.31 did not beat the random-matched-turnover baseline" to
"performance was disappointing."

## Attribution

Use:

- "the paper claims"
- "this run achieved"
- "the implementation assumes"
- "the evidence does not establish"
- "the audit could not evaluate"

Avoid collapsing these into one statement.

## Verdicts

### `scaffold-only`

Use when placeholder data or non-evidentiary outputs are present.

### `weak`

Use when central claims fail, critical red flags remain, or results do not beat
credible nulls and baselines.

### `inconclusive`

Use when evidence is mixed, key tests are unavailable, or implementation/data
differences prevent a clean interpretation.

### `promising`

Use only when material claims reproduce, the result survives nulls, costs,
multiple-testing correction, and robustness checks, and no critical red flag
remains.

## Fairness

Steelman plausible explanations for a failed reproduction. State the evidence
that would distinguish them. Do not soften a documented failure, but do not
overstate its scope.

## Final Paragraph

State:

1. verdict
2. decisive evidence
3. decisive unresolved risk
4. next test most likely to change the verdict
5. research-only disclaimer
