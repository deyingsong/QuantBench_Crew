---
name: empirical-spec-parser
description: Parse a paper's empirical design into datasets, sample construction, features, labels, preprocessing, splits, baselines, and evaluation metrics. Use when Reader must determine exactly what evidence was produced, assess comparability, or prepare a study for reproduction.
---

# Empirical Spec Parser

Turn the empirical study into a data-and-evaluation contract. Keep raw data,
derived variables, targets, metrics, and reported results conceptually
separate.

## Workflow

1. Read `references/empirical-design-reading.md`.
2. Inspect the methods, data section, tables, figures, captions, appendices,
   and result notes.
3. Extract datasets with provider, population or universe, unit of observation,
   sample period, filters, and access constraints.
4. Separate raw inputs from derived features, predictors, signals, and
   preprocessing.
5. Identify labels, outcomes, targets, forecast horizons, and construction
   rules.
6. Record train, validation, test, temporal, cross-sectional, and
   out-of-sample split rules.
7. Extract baselines and evaluation metrics; keep numeric findings out of the
   metric definition.
8. Attach evidence, preserve unknowns, and report confidence.

## Output Contract

Return a single JSON object with:

```json
{
  "datasets": [],
  "features": [],
  "labels": [],
  "preprocessing": [],
  "splits": [],
  "baselines": [],
  "metrics": [],
  "confidence": 0.0,
  "evidence": [{"field": "", "quote": ""}]
}
```

## Guardrails

- A database name is not a complete dataset specification.
- Do not call an outcome a feature or a reported value a metric definition.
- Treat temporal leakage, unavailable-at-decision-time data, and unclear
  sample filters as visible uncertainties.
- Do not infer conventional train/test splits when none are stated.
- Preserve units, horizons, transformations, and sample dates exactly.
