# Phase 2 Status

Status: complete
Date: 2026-06-11
Tests: 210 total, all passing (209 default + 1 eval gate; e2e 3/3). 37 test
files, 60 source modules. Run with the `quantbench-crew` conda env.

## Scope delivered (QB-17 .. QB-35)

Phase 2 turned the Phase 1 walking-skeleton-made-real into a system that
ingests papers at scale, audits their claims, reproduces them on real and free
data with statistical rigor, and regression-tests itself.

- **F — extraction & ingestion depth** (QB-17..21): live arXiv pagination +
  backoff + cross-run dedup; charter-relevance ranking; full-text MethodSpec
  extraction; falsifiable-claim enumeration; quant-pitfalls red-flag scan.
- **G — real data tiers** (QB-22/23): pure-stdlib streaming CRSP CIZ loader
  (survivorship-free, delisting-spliced, point-in-time monthly panel from the
  683 MB daily file); optional `numeric` dependency tier.
- **H — statistical rigor** (QB-24..28): deflated Sharpe (trial count from the
  manifest), capacity proxy, FF5+momentum spanning, multiple-testing
  correction, robustness (subsample + parameter sweep), and a reviewer verdict
  that now *requires* deflation survival + sign-stability + no critical red
  flag to call anything "promising".
- **I — generation depth** (QB-29..32): construction-aware spec invariants;
  vetted opt-in numerical sandbox; agentic codegen adapter (headless Claude,
  availability-gated); sandboxed walk-forward so untrusted generated code runs
  without host-side execution.
- **J — eval set + CI** (QB-33..35): self-regression harness, four curated
  cases, `pytest -m eval` gate.

## Run commands

```
# fast suite (eval deselected)
<env>/bin/python -m pytest -q
# the system regression gate (slow; runs CRSP cases when the data is present)
<env>/bin/python -m pytest -m eval -q
```

## Key empirical finding

On the operator's real 2015–2024 CRSP S&P 500 data, neither Jegadeesh–Titman
momentum nor the GKX-style linear ML cross-section clears the strict
reproduction bar: both beat the random null but **do not survive the
deflated-Sharpe correction** (momentum p=0.95, GKX p=0.85). The strong planted
synthetic signal does (p≈0); the pure-noise negative control does not. The
system correctly declines to over-claim — see
[phase2-design.md](phase2-design.md) → QB-34 "As built".

## Determinism policy

Two-tier, operator-confirmed: the stdlib dry workflow is bit-exact (identical
manifest content hash on rerun); the numeric/real-data paths are
tolerance-banded (pinned seeds, banded assertions). The eval harness compares
verdicts and banded metrics, not hashes.

## Out of scope / next

- **Value, profitability, full nonlinear GKX**: need Compustat fundamentals and
  the sklearn tier (the linear `ml` strategy is the price/volume placeholder).
- **The Ozimek PDF** (`data/raw/2606.08586v1.pdf`): a different, intraday TDA
  paper — out of scope unless its intraday data is supplied.
- **Agentic-codegen cost capture**: the agent path is iteration-bounded; wiring
  headless-Claude cost into the manifest's `llm_calls` is a follow-up.
- **Phase 3** (per the original note): parallel paper runs, LLM call caching,
  human-in-the-loop checkpoints before any "promising" verdict ships.
