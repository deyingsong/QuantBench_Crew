# Spec-Gap Detection And Reader-Consultation Protocol

## Purpose

A precise, deterministic account of *what counts as a gap* in a `MethodSpec`,
*how to phrase the question* to the Reader, and *what default to adopt* when the
source is silent. The Coder uses this to decide when to consult rather than
guess.

## What Counts As A Gap

A field is a gap when it is empty, contains a placeholder/vague marker, or is
low-confidence — and only when resolving it could change the weights the
strategy produces (a *performance-affecting* gap).

Placeholder/vague markers (case-insensitive): `""`, `not identified`,
`requires human review`, `unclear`, `n/a`, `unspecified`, `tbd`, `metadata-only`,
or a value hedged with "approximately / -ish / or so" on a parameter that needs
a number.

Required performance-affecting fields:

| Field | Why a gap here changes weights |
| --- | --- |
| `universe` | Determines which assets are eligible and the cross-section ranked. |
| `frequency` | Sets the bar size every feature and return is computed on. |
| `signal_definition` | The core function; ambiguity here changes every position. |
| `portfolio_construction` | Maps signal to weights; long-only vs long-short, weighting, leg sizing. |
| `rebalance_frequency` | Controls turnover and when positions update. |
| `holding_period` | Overlapping vs non-overlapping changes exposure and turnover. |

Also treat as gaps: `extraction_confidence` below the configured threshold
(default 0.5), and any required field with no supporting `evidence` link.

Non-gaps (do not consult): cosmetic naming, comment wording, or any choice the
spec explicitly sanctions a default for.

## Question Templates

Phrase each question so the Reader can answer from the paper, and attach the
Coder's grounded guess.

- **universe** — "What is the exact eligibility universe and its point-in-time
  filters (price, liquidity, listing)? GUESS: <spec hint or 'US common stocks,
  price > $5'>."
- **frequency** — "At what bar frequency are signals and returns computed?
  GUESS: <daily|weekly|monthly from spec hints>."
- **signal_definition** — "State the signal formula precisely, including window
  lengths and any skip period. GUESS: <best reading of the stated definition>."
- **portfolio_construction** — "Long-only or long-short? How are weights set
  (equal, value, rank) and legs sized? GUESS: <spec hint>."
- **rebalance_frequency / holding_period** — "How often are positions updated
  and how long are they held (overlapping?)? GUESS: <spec hint>."

## Default-Fallback Policy

When the Reader answers "unspecified in source":

1. Adopt the **neutral, declared default** for that field (e.g. equal-weight
   legs, non-overlapping monthly holding, US common stocks price > $5) — never
   the value that maximizes the candidate's score.
2. Record the default as an explicit assumption on the artifact, so the Bench
   and Reviewer see it and can stress it.
3. If no neutral default exists and the choice dominates the result, mark the
   reproduction as blocked on that field rather than guessing.

## Grounding Note

In `mode: harness` the consultation is a real Reader re-invocation against the
paper. In `mode: api` the seam routes the questions to the Reader backbone,
which answers from the distilled analysis fields (and full text when present) —
honest about its basis, and instructed to say "unspecified in source" rather
than invent. Either way, the Coder never fabricates an answer to its own
question.

## Provenance

The consult-then-default discipline distills the research-process consensus in
the corpus — separate collection from judgment, ground decisions in the primary
source, prefer an explicit "unknown" to a fluent guess, and keep an auditable
record — consistent with the Scout and Reader transcript-distilled references
already in this repository.
