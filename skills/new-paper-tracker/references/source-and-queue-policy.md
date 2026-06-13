# Source And Queue Policy

## Contents

- Date semantics
- Search protocol
- Deduplication
- Queue schema
- Failure handling
- Distilled research-practice principles

## Date Semantics

Use the first defensible day-level date on which the paper became publicly accessible online. Treat the window as inclusive.

- arXiv: use the submission/publication day returned by arXiv.
- OpenAlex journal record: use `publication_date` when day-level.
- DBLP conference record: a year alone is not an exact online date; exclude it from strict windows and report it as missing exact date.
- Local record: accept `online_date` or `published` only when it parses as `YYYY-MM-DD`.
- Never substitute ingestion date, current date, issue year, or a guessed month/day.

## Search Protocol

Record the window, assigned sources, query or query-pool, result budget, and failures. Apply the same conceptual search intent across sources while respecting each source's syntax.

Push the exact date window into a source API when it supports date filtering,
then verify dates locally. Result budgets still bound coverage; report the
budget so "all" means all records returned under the declared search protocol,
not an unbounded claim about the source.

Set `OPENALEX_API_KEY` for journal monitoring and DBLP abstract enrichment.
Treat missing credentials or provider rejection as a visible source failure.

Use broad discovery followed by explicit screening:

1. Define the research charter and inclusion/exclusion rules before seeing results.
2. Search assigned databases plus relevant grey literature or preprint sources.
3. Deduplicate before screening.
4. Screen date and charter fit.
5. Rank survivors; do not rewrite inclusion rules to favor an exciting result.
6. Preserve enough information to rerun and explain the search.

## Deduplication

Match in this order:

1. DOI
2. arXiv id
3. canonical URL
4. normalized-title hash

When records collide, retain the record with the richest abstract, author list, and raw metadata. Do not count versions of one paper as independent evidence.

## Queue Schema

The repository queue is JSON with `schema_version`, allowed `statuses`, and `entries`.

Each entry contains:

- stable `id`
- title, abstract, authors, source, URL, online date
- current score, rank, reasons, and detailed assessment
- status and human notes
- first/last seen dates
- latest search window

Statuses:

- `queued`: discovered and awaiting a decision
- `promoted`: approved for close reading or reproduction
- `deferred`: relevant, but not worth current capacity
- `rejected`: explicitly screened out
- `analyzed`: downstream analysis completed

Refresh metadata and scores, but preserve status, notes, and first-seen date.

## Failure Handling

Report source failures and missing dates. An empty result set can mean no papers, a narrow query, a source outage, a rate limit, or incomplete metadata. Do not collapse these into the same conclusion.

## Distilled Research-Practice Principles

The academic and systematic-review transcript groups repeatedly converge on:

- predeclare the question and screening rules;
- search broadly, then filter explicitly;
- treat tools and AI as accelerators, not sources of truth;
- verify citations and retain provenance;
- keep a single accessible record of notes and decisions;
- stop early on low-value material and spend depth only on survivors.

These principles are operationalized here as strict dates, visible exclusions, a durable queue, and preserved decisions.
