---
name: criticizer
description: Critically evaluate a research paper by identifying explicit and implicit assumptions, author-stated limitations, validity threats, unanswered questions, and limitation-grounded future directions. Use when Reader must test a paper's logic, scope, evidence, or generalizability.
---

# Research Criticizer

Test the paper's argument rather than merely summarize it. Criticism should
identify what must be true, what the evidence cannot establish, and what would
change the conclusion.

## Workflow

1. Read `references/critical-reading.md`.
2. State the central claim and the evidence used to support it.
3. Identify explicit and implicit assumptions in the argument, model, data,
   measurement, and evaluation design.
4. Separate author-stated limitations from Reader-inferred validity threats.
5. Ask what alternative explanation, missing comparison, or omitted evidence
   could overturn the conclusion.
6. Ask what observation would falsify the central claim and what is required
   to generalize it.
7. Derive future directions from a named limitation or unanswered question,
   not from generic novelty suggestions.
8. Attach evidence and lower confidence where critique depends on missing
   full text or unstated design details.

## Output Contract

Return a single JSON object with:

```json
{
  "assumptions": [],
  "author_stated_limitations": [],
  "reader_inferred_threats": [],
  "unanswered_questions": [],
  "future_directions": [],
  "confidence": 0.0,
  "evidence": [{"field": "", "quote": ""}]
}
```

## Guardrails

- Do not invent flaws merely to appear critical.
- Separate absence of reporting from proof that a procedure was not done.
- Distinguish internal validity, external validity, construct validity, and
  reproducibility.
- Make future work answer a concrete limitation or unresolved question.
- Prefer a few consequential critiques over a generic checklist.
