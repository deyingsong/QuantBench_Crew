# QuantBench_Crew Engineering Standards

This `CLAUDE.md` establishes the baseline behavior for Claude Code within the `QuantBench_Crew` repository. 

## 1. Core Engineering Values & Domain Rules
* **Scientific Rigor:** This is a multi-agent system evaluating quantitative finance research. Maintain strict temporal and point-in-time data discipline. Never mask failures, suppress errors, or fabricate backtest results.
* **Separation of Concerns:** Keep LLM orchestration and agent prompt logic strictly decoupled from business logic. Core execution domains—such as statistical arbitrage models, performance benchmarking, and C++ or Python backtesting engines—must remain modular, stateless, and mathematically pure.
* **Surgical Precision:** Touch only the files necessary to resolve the current task. Do not make speculative features, over-engineer abstractions, or "improve" unrelated adjacent code.

## 2. Refactoring & Code Cleanup
When instructed to clean up or refactor messy code, YOU MUST systematically apply these principles:
* **Eradicate Noise:** Delete commented-out code, dead imports, and obsolete helper functions. Do not leave "TODO" placeholders. Replace `print()` statements with structured `logging`.
* **Vectorize:** Eliminate manual `for`-loops over datasets. You must use vectorized `pandas` and `numpy` operations for all financial data manipulation. Machine learning and PyTorch components should utilize batched operations optimized for hardware acceleration.
* **Decouple Monoliths:** Break down massive functions into focused, single-responsibility units. 

## 3. Python Standards (Python 3.11+)
* **Typing:** YOU MUST enforce comprehensive type hints (`typing` module) for all function arguments and return values.
* **Documentation:** Use concise NumPy-style docstrings for public classes and functions. 
* **Formatting:** Do not format manually. Rely on standard standard tooling; run the project's linter and formatter (e.g., `ruff check --fix` and `black`) before completing your task. 

## 4. Verification & Workflow
* **Verify Before Committing:** Never assert success blindly. If fixing a bug, write a test that reproduces it, fix the bug, and run `pytest tests/` to confirm. 
* **Provide Evidence:** Always output the explicit results of your test runs or sandbox executions.
* **Think Before Coding:** If a requirement regarding the methodology extraction, agent skills, or the evaluation pipeline is ambiguous, STOP and ask for clarification rather than guessing.