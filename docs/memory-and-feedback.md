# Human Feedback And Persistent Memory

QuantBench Crew treats expert feedback and cross-session memory as governed
evidence. A report comment does not silently rewrite a prompt, and a model
cannot promote its own observation into permanent guidance.

## Human feedback lifecycle

Every generated report ends with a bounded editable section:

```markdown
## Human proofreading notes
<!-- quantbench:feedback:start -->
Write expert comments here.
<!-- quantbench:feedback:end -->
```

Regenerating `reports/<paper-slug>.md` preserves the text inside these markers.
The surrounding report can change without erasing or duplicating the notes.

Ingest the notes:

```bash
quantbench feedback ingest reports/<paper-slug>.md
quantbench feedback list --status proposed
```

Ingestion is idempotent. It stores the raw text, report hash, source path,
paper identity, deterministic category, proposed scope, and change proposal.
The supported categories are:

- `factual_correction`
- `method_gap`
- `bug`
- `style`
- `process_guidance`

Nothing from a proposed record is shown to an agent. An expert or operator
must approve it:

```bash
quantbench feedback approve <feedback-id> --reviewer "name"
```

Approval creates an active memory with immutable provenance back to the raw
feedback. Rejection keeps the audit record but prevents recall:

```bash
quantbench feedback reject <feedback-id> --reviewer "name"
```

Use `--category`, `--scope`, `--scope-key`, and `--agent` during ingestion to
override the deterministic classification.

## SQLite memory

The default database path is:

```text
data/quantbench_memory.sqlite3
```

It contains:

- run summaries and agent/skill events;
- episodic, semantic, procedural, and prospective memories;
- feedback and change-proposal approval state;
- consolidation records and archive indexes.

Run artifacts and manifests remain the canonical evidence. SQLite indexes the
history and connects records across runs.

Memory recall is disabled in the shipped config. Enable it per run:

```bash
quantbench run --use-memory
```

Or set:

```yaml
memory:
  enabled: true
  path: data/quantbench_memory.sqlite3
  recall_limit: 8
```

Only `approved` memories are recalled. Scope may be `global`, `agent`,
`paper`, or `agent_paper`. Recalled content is appended to the relevant
agent's system context with a warning that it is operating guidance rather
than paper evidence. Every recalled memory ID and content hash is recorded in
the run manifest.

Useful commands:

```bash
quantbench memory inspect
quantbench memory remember "Use point-in-time constituents." \
  --kind procedural
quantbench memory approve <memory-id>
quantbench memory recall --agent quant_reader --query "constituents"
```

Explicit operator memories default to `proposed`. Approve them separately, or
pass `--status approved` when the operator intends immediate activation.

## Consolidation and archiving

Monthly consolidation is deterministic:

```bash
quantbench memory consolidate --month 2026-06
```

It counts recorded activity, identifies failed skills, supersedes exact
duplicate memories, and creates a descriptive monthly digest. The digest does
not invent or activate new procedural rules.

Archive cold history after 90 days:

```bash
quantbench memory archive --older-than-days 90
```

Old events and approved episodic memories are copied into quarterly SQLite
archives under `data/archive/`. Approved procedural/semantic guidance and
prospective unresolved work remain active. Raw feedback is retained.

These commands are safe to schedule externally. They are not automatically
scheduled by the application.

## Hermes integration boundary

`HermesMemoryAdapter` accepts a deployment-specific client exposing
`remember(record)` and `recall(memory_id)`. Every write performs a
read-after-write content check. A missing or mismatched read raises an error;
the system never treats an unverified cross-agent delivery as successful.
