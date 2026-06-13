---
name: relevance-scorer
description: Rank quantitative-finance papers by likely downstream research value using charter fit, empirical evidence, implementability, economic relevance, information gain, disclosed risks, and metadata confidence. Use when Scout must prioritize candidate papers, explain a ranking, select papers for close reading, or decide where reproduction effort is worth spending.
---

# Relevance Scorer

Estimate whether a paper deserves scarce downstream attention. Do not confuse a compelling abstract with validated alpha.

## Workflow

1. Read `references/scoring-rubric.md` before scoring or changing weights.
2. For nuanced interpretation, read `references/transcript-distillation.md`. Use its expert lenses as questions, never authority bonuses.
3. Score only disclosed evidence. Mark absent information as unknown; do not invent data access, code availability, costs, or robustness.
4. Apply the staged-reading rule:
   - Pass 1: title, keywords, abstract, conclusion if available.
   - Pass 2 only for survivors: figures, tables, captions, claims, baselines.
   - Pass 3 only for promoted papers: methods, data construction, implementation details.
5. Return a 0-1 research-value score, dimension scores, positive signals, penalties, confidence, and a short rationale.
6. Prefer papers that can change a decision or test a live research belief. Penalize papers that merely optimize a fashionable model on a familiar dataset.

## Run The Deterministic Scorer

```bash
python skills/relevance-scorer/scripts/score_papers.py \
  --paper-json papers.json \
  --agents-config configs/agents.yaml
```

## Non-Negotiables

- Charter fit gates attention; general interestingness is not enough.
- Reward explicit out-of-sample tests, realistic costs, baselines, robustness, accessible data, released code, and implementable detail.
- Ask what mechanism could sustain the result, who is on the other side, and why competition has not erased it.
- Ask how the idea changes portfolio exposures, drawdown, capacity, or regime dependence.
- Penalize hidden trial counts, in-sample-only claims, vague abstracts, inaccessible data, missing costs, and brittle complexity.
- Keep score and confidence separate. A high-potential paper with sparse metadata may rank well but must carry low confidence.
