---
name: new-paper-tracker
description: Track newly online research papers from assigned sources within an explicit date window, deduplicate them, rank them with Scout's relevance scorer, and maintain a durable analysis queue. Use for recurring paper surveillance, date-bounded literature searches, source monitoring, or updating the Scout paper queue.
---

# New Paper Tracker

Build an auditable candidate funnel before spending effort on full-text reading or reproduction.

## Workflow

1. Require inclusive `YYYY-MM-DD` start and end dates. Never guess the year from inputs such as "May 31 - June 10".
2. Read `references/source-and-queue-policy.md` before changing sources, date semantics, deduplication, or queue states.
3. Search every assigned source with the same declared query or query-pool intent.
4. Keep only records with a defensible day-level online date inside the window. Report records missing an exact date separately; do not silently include them.
5. Deduplicate in this order: DOI, arXiv id, canonical URL, normalized-title hash. Prefer the richer metadata record.
6. Rank the in-window set with `$relevance-scorer`. Ranking is triage, not proof.
7. Upsert the durable queue. Preserve existing human status and notes across refreshes.
8. Report source coverage, discovered/unique/in-window/missing-date counts, queue additions/updates, and the ranked shortlist.

## Run The Repository Workflow

```bash
python skills/new-paper-tracker/scripts/track_papers.py \
  --start-date 2026-05-31 \
  --end-date 2026-06-10 \
  --source arxiv \
  --source journals \
  --query-pool auto
```

The command updates `data/processed/paper_queue.json` unless `--queue-path` is supplied.

## Queue Discipline

- Use `queued` for new candidates, `promoted` for papers approved for close reading, `deferred` for promising but mistimed work, `rejected` for explicit no-go decisions, and `analyzed` after downstream review.
- Never erase a prior human status or note during a refresh.
- Keep rejected and analyzed entries in the queue history so repeated searches remain explainable.
- Treat source failures, missing dates, and empty result sets as visible outcomes, not evidence that no papers exist.
