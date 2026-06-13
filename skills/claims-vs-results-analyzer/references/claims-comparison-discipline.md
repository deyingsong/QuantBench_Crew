# Claims Comparison Discipline

## Unit Of Analysis

The unit is a falsifiable paper claim, not the paper as a whole. Capture:

- metric and direction
- claimed value and tolerance
- sample, universe, horizon, and portfolio construction
- gross or net-of-cost basis
- in-sample, validation, or out-of-sample status
- paper source
- achieved value and run artifact

## Matching Hierarchy

Before comparing values, verify:

1. Same metric definition and annualization.
2. Same target, label horizon, and lag convention.
3. Same universe and eligibility filters.
4. Same sample period or an explicitly labeled extension.
5. Same weighting, rebalance, holding, and overlap rules.
6. Same transaction-cost and financing assumptions.
7. Same model-selection and trial-count treatment.

If any item differs materially, report the comparison but classify the mismatch
as a possible explanation.

## Status Rules

- `reproduced`: achieved value is within the declared tolerance under a
  materially comparable design.
- `not_reproduced`: a comparable test was run and fell outside tolerance.
- `not_evaluated`: no comparable test exists, the metric is missing, or the
  design mismatch is too large to interpret.

Never convert `not_evaluated` into a negative result. Never convert one
successful metric into validation of all claims.

## Gap Diagnosis

Investigate in this order:

1. Extraction ambiguity: equations, tables, or definitions may have been read
   incorrectly.
2. Implementation ambiguity: tie-breaking, missing-value rules, lags, and
   portfolio construction may differ.
3. Data provenance: versions, survivorship, corporate actions, vendor fields,
   and timestamps may differ.
4. Evaluation protocol: splits, embargoes, tuning, baselines, costs, and trial
   counts may differ.
5. Statistical uncertainty: sampling error and regime dependence may explain
   the gap.
6. Empirical failure: only after the earlier explanations are reasonably
   excluded.

## Reproducibility Issues To Surface

- no implementable method specification
- no quantitative target or source table
- inaccessible proprietary data
- undisclosed transformations or hyperparameters
- target leakage or timestamp ambiguity
- uncounted model-selection trials
- no realistic cost or capacity analysis
- no simple, random, or incumbent baseline
- failed or unavailable stress tests
- results sensitive to one sample, seed, or parameter

## Output Pattern

Lead with a claim table. Follow with:

1. implementation issues
2. reproducibility issues
3. most plausible gap explanations
4. decisive next tests

Use language such as "this run did not reproduce" rather than "the paper is
wrong" unless the evidence genuinely supports the stronger statement.

## Corpus-Derived Priorities

The requested practitioner corpus reinforces this protocol:

- Jane Street and institutional quant interviews elevate inspectable
  implementation, edge cases, and adversarial review.
- Christina Qi, Igor Tulchinsky, Richard Craib, Jim Simons, and David Shaw
  material emphasizes separating repeatable process from lucky outcomes.
- Dimitri Bianco and model-risk material emphasizes limitations, monitoring,
  ownership, and controls.
- Lopez de Prado and Niederhoffer material emphasizes trial disclosure,
  selection bias, and falsification.
- Ernest Chan and trading-practitioner interviews emphasize timestamps, costs,
  fills, capacity, and out-of-sample realism.
- The governance-failure material warns that narratives and apparent profits
  cannot substitute for provenance, controls, and auditability.

These are diagnostic priorities, not substitutes for the paper and run
evidence.
