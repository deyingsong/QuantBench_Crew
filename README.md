# QuantBench Crew

QuantBench Crew is a multi-agent research assistant for discovering, reproducing, and benchmarking quantitative finance papers.

It is designed to help researchers move from paper discovery to method extraction, implementation planning, empirical benchmarking, and final review in a reproducible way. It does not make trading decisions, execute trades, or provide financial advice.

## Current Status

This repository contains an initial runnable backbone:

- Agent classes for scouting, reading, ERA-backed coding, benchmarking, and reviewing papers.
- Tooling for loading paper metadata, parsing paper-like records, running local commands, and evaluating benchmark results.
- YAML/JSON configuration loading.
- A command-line entry point for a dry workflow.
- Starter tests and project structure for future development.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Configure

```bash
cp .env.example .env
```

Then adjust values such as:

```text
OPENAI_API_KEY=your_api_key_here
ARXIV_QUERY=quantitative finance
DATA_DIR=./data
REPORT_DIR=./reports
```

The first version does not require an API key for the dry workflow.

The coder agent uses an ERA-style Flat UCB Tree Search adapter with deterministic
QuantBench generators and scoring, so it stays runnable without Gemini or other
LLM credentials. Live ERA generation and sandbox execution can be connected
behind the same `generate_fn` and `execute_fn` interface later.

## Run

Run the default local workflow:

```bash
python -m quantbench_crew.main
```

Or use the installed CLI:

```bash
quantbench run --source local --max-papers 2
```

Write reports to disk:

```bash
quantbench run --query "asset pricing machine learning" --max-papers 3 --write-reports
```

## Test

```bash
pytest
```

## Repository Layout

```text
configs/              Agent, task, and benchmark defaults.
data/                 Raw, processed, and benchmark data placeholders.
docs/                 Design notes and project documentation.
reports/              Generated research reports.
src/quantbench_crew/  Python package.
tests/                Unit tests.
```

## Disclaimer

QuantBench Crew is a research-support tool. Outputs must be reviewed by qualified human researchers before being used in any investment, trading, risk management, or production decision-making process.
