# Parsing Empirical Design

## Transcript-Distilled Method

Systematic-review guidance emphasizes defining the question and inclusion
rules before comparing studies, then separating study characteristics from
findings. Apply that discipline inside each paper: extract the design first,
then interpret the reported results.

Tables, figures, captions, footnotes, data sections, and appendices often carry
the most precise empirical definitions. Read them as part of the specification,
not as decoration.

## Data Contract

For every dataset, seek:

- source/provider and version;
- population, universe, geography, and unit of observation;
- sample start/end dates and observation frequency;
- inclusion/exclusion filters and missing-data handling;
- merge keys, timing, lags, and availability at decision time;
- access restrictions and reproducibility constraints.

For variables, distinguish:

- raw data;
- preprocessing and transformations;
- features, predictors, covariates, or signals;
- labels, outcomes, targets, and forecast horizons.

For evaluation, distinguish:

- train/validation/test and temporal split rules;
- out-of-sample, cross-validation, walk-forward, or holdout design;
- baselines and ablations;
- metric definitions and units;
- numeric findings, which belong to claims rather than metric definitions.

## Evidence Discipline

Use structured, searchable notes and preserve source locations. AI can speed
extraction but must not invent a split, variable construction, or metric that
the primary paper does not state. Mark reporting gaps explicitly.

## Provenance

Distilled from all requested academic/research transcript folders, especially
the systematic-review, research-tools, AI-in-academia, reading/writing, and
knowledge-acquisition playlists.
