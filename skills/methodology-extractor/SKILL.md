---
name: methodology-extractor
description: Reconstruct a paper's proposed methodology, equations, algorithms, and experiment settings while separating the new method from baselines and omitted details. Use when Reader must explain how a study answers its question or prepare a paper for implementation review.
---

# Methodology Extractor

Trace the chain from research question to method choice, mathematical
definition, algorithm, and experiment. Preserve what the authors specify and
make omissions visible.

## Workflow

1. Read `references/method-reading.md`.
2. Survey figures, tables, captions, results, and discussion before spending
   deep attention on methods.
3. Identify the proposed method and its claimed role in answering the question.
4. Extract equations with symbol meanings, objective functions, constraints,
   and transformations.
5. Reconstruct algorithms in execution order, including initialization,
   training or estimation, inference, and decision rules.
6. Extract experiment settings separately from datasets and labels: parameter
   choices, frequency, horizons, software, hardware, random seeds, and
   robustness variants.
7. Separate proposed method, baselines, implementation details, and
   unspecified steps.
8. Attach evidence and report confidence.

## Output Contract

Return a single JSON object with:

```json
{
  "summary": "",
  "equations": [],
  "algorithms": [],
  "experiment_settings": [],
  "baselines": [],
  "omitted_details": [],
  "confidence": 0.0,
  "evidence": [{"field": "", "quote": ""}]
}
```

## Guardrails

- Preserve notation; do not silently simplify formulas.
- Never fill an omitted algorithm step with common practice.
- Distinguish the authors' method from a baseline or ablation.
- Do not confuse a result with a method.
- Keep this scientific-method summary distinct from the coder-facing
  `MethodSpec`, which requires an implementable trading specification.
