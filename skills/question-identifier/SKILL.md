---
name: question-identifier
description: Extract a paper's central research question, field state, importance, existing-method gap, and claimed contribution. Use when Reader must orient a paper, compare it with prior literature, or decide what problem the method and evidence are meant to solve.
---

# Question Identifier

Recover the paper's argument before reading its mechanics. A topic is not a
research question, and author enthusiasm is not evidence of importance.

## Workflow

1. Read `references/question-and-gap-reading.md`.
2. Survey the title, keywords, abstract, conclusion, figures, and captions.
3. Read the introduction closely enough to reconstruct the scholarly
   conversation: what is known, disputed, or missing.
4. State one central research question in answerable form.
5. Separate:
   - `field_state`: what existing research currently claims or does;
   - `importance`: the consequence of answering the question;
   - `existing_method_gap`: what current evidence or methods fail to do;
   - `claimed_contribution`: the paper's proposed answer or reusable idea.
6. Attach a short source excerpt or location to every substantive claim.
7. Label inferred interpretations and lower confidence when the paper does not
   state an element explicitly.

## Output Contract

Return a single JSON object with:

```json
{
  "question": "",
  "field_state": [],
  "importance": [],
  "existing_method_gap": [],
  "claimed_contribution": [],
  "confidence": 0.0,
  "evidence": [{"field": "", "quote": ""}]
}
```

## Guardrails

- Prefer one precise question over a list of topics.
- Distinguish an evidence gap from a method weakness, scope limitation, or
  unresolved contradiction.
- Do not infer importance from novelty alone.
- Do not treat the abstract's framing as an objective map of the field.
- Return unknowns instead of repairing a weakly framed paper.
