# Architecture

QuantBench Crew starts with five small, composable agents:

1. `QuantScoutAgent` loads candidate papers and ranks them by relevance.
2. `QuantReaderAgent` extracts a structured summary and method notes.
3. `QuantCoderAgent` uses an ERA-style Flat UCB Tree Search loop to create an implementation plan.
4. `QuantBenchAgent` produces benchmark result records.
5. `QuantReviewerAgent` writes the final review.

The first implementation is intentionally deterministic. The coder already follows ERA's `Problem`, `Solution`, `generate_fn`, and `execute_fn` shape, but the local adapter generates and scores structured implementation plans instead of calling an LLM or sandbox. External services such as arXiv, LLM APIs, PDF parsing, vector stores, and experiment runners can be connected behind the existing tools and agent interfaces later.

## Data Flow

```text
Paper source -> Scout -> Reader -> Coder -> Bench -> Reviewer -> Markdown report
```

## Design Constraints

- Research support only, not autonomous trading.
- Reproducible configs and report artifacts.
- Human-readable output at each stage.
- Clear extension points for future paper ingestion and benchmarks.
