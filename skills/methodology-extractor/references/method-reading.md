# Reading Scientific Methods

## Transcript-Distilled Method

Expert readers do not begin by reading every methods paragraph. They first
survey the abstract, conclusion, figures, tables, captions, results, and
discussion to learn what method details matter. Deep methods reading is then
guided by the paper's central claim.

Reconstruct this chain:

`research question -> method choice -> mathematical definition -> algorithm -> experiment -> result`

Writing is part of research because it exposes missing logic. Apply the same
pressure while reading: if the method cannot be outlined coherently, record
the missing link rather than repairing it.

## Extraction Checklist

- Proposed method and purpose
- Inputs, outputs, state, and decision rules
- Equations, symbols, objectives, constraints, and transformations
- Algorithm steps in execution order
- Estimation, optimization, training, inference, and stopping rules
- Parameter settings, horizons, frequencies, seeds, software, and hardware
- Baselines, ablations, robustness variants, and sensitivity tests
- Details deferred to appendices, supplements, code, or prior work
- Omitted information required to understand or reproduce the method

## Distinctions

- Method versus result: "uses ridge regression" is method; "improves RMSE" is
  result.
- Proposed method versus baseline: preserve each role.
- Scientific method versus trading implementation: this skill explains the
  study design; `MethodSpec` supplies the coder-facing trading contract.
- Explicit versus conventional: never substitute usual practice for missing
  detail.

## Provenance

Distilled from the requested academic/research transcript folders, with
particular weight on Pete Carr's staged-reading workflow, George Whitesides'
outline-and-hypothesis method, paper-writing guidance, systematic-review
analysis, and source-verification guidance from AI/research-tool videos.
