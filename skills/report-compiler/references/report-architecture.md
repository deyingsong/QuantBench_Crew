# Report Architecture

## Purpose

The final report should let a research lead decide what has been learned, what
has not been learned, and what experiment deserves resources next. It is not a
paper summary and not a sales pitch.

## Required Sections

### 1. Decision Summary

State:

- verdict
- number of claims reproduced, failed, and not evaluated
- strongest supporting evidence
- most important unresolved threat
- scope: this reproduction attempt, not universal truth

### 2. Paper Thesis And Claimed Contribution

Give the research question, field gap, proposed mechanism, and claimed
increment over existing methods. Separate author claims from Reviewer
inference.

### 3. Claims Versus Reproduced Results

Use a table with:

| Metric | Claimed | Achieved | Gap | Tolerance | Status | Evidence |
| --- | ---: | ---: | ---: | ---: | --- | --- |

Label design mismatches and untested claims. Never hide them in prose.

### 4. Empirical Findings

Report primary metrics, baseline comparisons, multi-dataset expectations, and
claim comparisons. Distinguish:

- statistical performance
- net-of-cost economic performance
- portfolio contribution

### 5. Implementation And Reproducibility

List missing specifications, data constraints, interpretation choices, and
provenance gaps. Explain whether each issue could plausibly account for a
claim gap.

### 6. Robustness And Risk

Cover:

- out-of-sample and walk-forward design
- multiple-testing correction and trial disclosure
- subsample, seed, parameter, regime, and cost sensitivity
- drawdown, leverage, liquidity, capacity, and risk of ruin
- failed and unavailable checks

### 7. Economic And Portfolio Interpretation

Ask why the edge could persist, who pays for it, how crowded it may be, and
whether it adds value beyond simple or existing exposures. Report factor
spanning, correlation, turnover, and capacity when available.

### 8. Expert Lens Review

Apply multiple lenses independently. Name tensions explicitly. A strategy may
look statistically credible but operationally weak, or economically plausible
but redundant in a portfolio.

### 9. Strengths And Weaknesses

Strengths require evidence. Weaknesses should be prioritized by how directly
they threaten the headline claim.

### 10. Open Questions And Decisive Next Tests

Turn uncertainty into experiments. Each proposed test should say what result
would upgrade, preserve, or downgrade the verdict.

### 11. Verdict And Scope

Use the configured verdict vocabulary. State why the evidence clears or fails
the relevant threshold. Add the research-only disclaimer.

## Evidence Discipline

- Cite artifact paths, manifest entries, table references, or paper passages.
- Keep author claims separate from reproduced results.
- Keep missing evidence visible.
- Do not average away a critical failure with many weak positives.
- Preserve contradictory results and failed trials.
