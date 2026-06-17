# Architecture

QuantBench Crew starts with five small, composable agents:

1. `QuantScoutAgent` loads candidate papers and ranks them by relevance.
2. `QuantReaderAgent` uses PaperQA2 to retrieve evidence from local documents and extract structured method notes.
3. `QuantCoderAgent` uses an ERA-style Flat UCB Tree Search loop to create an implementation plan.
4. `QuantBenchAgent` produces benchmark result records.
5. `QuantReviewerAgent` writes the final review.

The first implementation is intentionally deterministic when optional packages or document files are absent. The reader uses PaperQA2's `Docs` query interface when a paper record points to local files; otherwise it falls back to metadata extraction. The coder already follows ERA's `Problem`, `Solution`, `generate_fn`, and `execute_fn` shape, but the local adapter generates and scores structured implementation plans instead of calling an LLM or sandbox. External services such as arXiv, LLM APIs, PDF parsing, vector stores, and experiment runners can be connected behind the existing tools and agent interfaces later.

## Data Flow

```text
Approved memory -> RunContext -> Scout -> Reader -> Coder -> Bench -> Reviewer
                                      ^                              |
Paper source -------------------------+                              v
                              Markdown report -> human notes -> approval
                                                          -> persistent memory
```

## Design Constraints

- Research support only, not autonomous trading.
- Reproducible configs and report artifacts.
- Human-readable output at each stage.
- Clear extension points for future paper ingestion and benchmarks.
- Human feedback is immutable evidence before it becomes approved guidance.
- Persistent memory is scoped, provenance-linked, and recorded in manifests.

## Further Reading

- [skills-design.md](skills-design.md): proposed per-agent skill model, new domain dataclasses, and the Phase 1 ticket breakdown.
