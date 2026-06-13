---
name: robustness-auditor
description: Conduct and audit quantitative-strategy robustness checks across costs, parameters, subsamples, paths, regimes, and datasets while preserving experiment configurations and results. Use when Bench must determine whether a backtest is fragile, reproduce a stress-test ledger, disclose trial counts, or explain why a strategy should or should not survive deployment.
---

# Robustness Auditor

Treat robustness as evidence accumulated across adversarial perturbations.
Track every experiment so failed tests cannot disappear from the story.

## Workflow

1. Read `references/robustness-discipline.md`.
2. Freeze the base strategy, dataset, metric definitions, and acceptance rules.
3. Create an experiment ledger before running perturbations.
4. Audit subsample sign stability and parameter sensitivity.
5. Stress realistic and conservative transaction-cost assumptions.
6. Test alternate paths, seeds, regimes, universes, and datasets when
   available.
7. Inspect deflated Sharpe, disclosed trial count, drawdown, tail risk,
   capacity, leverage, and risk of ruin.
8. Hash configurations and results; retain failures and missing checks.
9. Separate:
   - robustness checks that passed;
   - checks that failed;
   - checks that could not be run;
   - assumptions that remain untested.
10. Prefer a conservative conclusion when stress evidence conflicts.

## Output Contract

Return:

- an experiment ledger with unique names, configurations, results, and verdicts;
- configuration and result hashes;
- passed, failed, and unavailable checks;
- cross-dataset and cost-stress conclusions;
- a concise robustness verdict grounded in recorded evidence.

## Guardrails

- Never reuse a holdout after inspecting and modifying the strategy.
- Do not call parameter instability a discovery opportunity.
- Monte Carlo or generated scenarios inherit modeling assumptions; disclose
  them and preserve dependence where possible.
- Stress tests must include plausible adverse conditions, not only friendly
  variations.
- Robustness cannot prove future profitability; it can expose fragility.
