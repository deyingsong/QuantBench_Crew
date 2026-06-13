---
name: claims-vs-results-analyzer
description: Compare a quantitative paper's claims with benchmark and reproduction results, then diagnose implementation and reproducibility issues. Use after Bench has produced metrics, claim comparisons, experiment results, or a robustness audit.
---

# Claims Vs Results Analyzer

Build a forensic comparison ledger before writing a narrative review. Separate
what the paper claims, what this run achieved, and what remains untested.

## Workflow

1. Enumerate every extracted quantitative claim and its source.
2. Match each claim to the same metric, unit, sample, portfolio, and cost basis.
3. Classify it as `reproduced`, `not_reproduced`, or `not_evaluated`.
4. Record claimed value, achieved value, tolerance, gap, note, and evidence.
5. Diagnose possible causes of gaps:
   - paper ambiguity or omitted details
   - implementation mismatch
   - inaccessible or changed data
   - evaluation mismatch
   - genuine empirical failure
6. Surface failed and unavailable robustness checks.
7. Preserve uncertainty. A failed reproduction is not by itself proof that the
   paper is false.

## Required Discipline

- Compare like with like; never compare gross with net, in-sample with
  out-of-sample, or a different universe without labeling the mismatch.
- Treat missing tests as `not_evaluated`, never as success.
- Link each finding to paper and run evidence.
- Report implementation questions and provenance gaps before assigning blame.
- Prefer a compact table plus a prioritized issue list.

Read [claims-comparison-discipline.md](references/claims-comparison-discipline.md)
for the detailed diagnostic protocol.
