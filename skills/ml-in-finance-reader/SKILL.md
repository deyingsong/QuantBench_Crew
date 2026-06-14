---
name: ml-in-finance-reader
description: Read and adversarially review machine-learning and deep-learning research applied to financial markets. Use for market-ML papers involving time-series forecasting, transformers, RNNs/LSTMs, foundation models, zero/few-shot adaptation, generative models, state-space models, graph or spatio-temporal models, explainable AI, multimodal systems, or AI agents; scrutinize temporal train/validation/test splits, point-in-time features, leakage, low-signal overfitting, baselines, multiple testing, implementation realism, and genuinely out-of-sample Sharpe.
---

# ML in Finance Reader

Analyze a market-ML paper as a chain from information available at a decision
time to a model, decision rule, executable position, and net out-of-sample
outcome. Architecture novelty never repairs a compromised information set or
evaluation protocol.

## Routing

Treat a paper as in-domain when ML or DL is central to a claim about financial
forecasting, classification, representation learning, synthetic data,
portfolio decisions, risk, execution, research automation, or market agents.

Also use this skill when a general time-series or AI method is proposed for
market transfer. In that case, separate the method's generic evidence from the
finance-specific evidence still required.

When invoked by Reader, reconstruct the paper faithfully before criticizing
it. When invoked by Reviewer, challenge the result with the paper, code, data,
and run artifacts. Preserve any stricter caller schema.

## Reference Router

Start with [references/index.md](references/index.md), then load only relevant
topic indexes and paper distillations:

- AI agents and autonomous tool use:
  [AI-agent/index.md](references/AI-agent/index.md)
- Explainability and temporal interpretation:
  [explainable-ai/index.md](references/explainable-ai/index.md)
- Direct financial LLM and multimodal applications:
  [finance-ai/index.md](references/finance-ai/index.md)
- GANs, VAEs, diffusion, and synthetic data:
  [generative-model/index.md](references/generative-model/index.md)
- Graph time-series models:
  [graph-model/index.md](references/graph-model/index.md)
- Pretrained and foundation models:
  [pretrained-foundation-model/index.md](references/pretrained-foundation-model/index.md)
- RNNs, transformers, and temporal point processes:
  [sequence-model/index.md](references/sequence-model/index.md)
- Spatio-temporal methods:
  [spatio-temporal-model/index.md](references/spatio-temporal-model/index.md)
- S4, Mamba, and other state-space models:
  [state-space-model/index.md](references/state-space-model/index.md)
- Core time-series methodology:
  [time-series-analysis/index.md](references/time-series-analysis/index.md)

Each paper distillation separates source-stated scope from finance-reader audit
questions. Verify decisive claims in the original PDF, tables, appendices, and
code.

## Workflow

### 1. Establish Evidence And Claim

Record the paper version, publication and working-paper dates, appendices,
code, model versions, data, and available run artifacts. Identify the central
claim and whether it concerns forecast accuracy, economic value, causal
insight, representation transfer, efficiency, or automation.

Separate:

- source-stated facts and results;
- reader inference;
- missing evidence;
- generic AI evidence versus market-specific evidence.

### 2. Define The Prediction Clock

Reconstruct one prediction or decision end to end:

- decision timestamp and market clock;
- target, horizon, and label construction;
- feature observation, publication, revision, and processing times;
- model fit, retraining, prompt, retrieval, and inference times;
- trade formation, execution price, latency, and holding period.

Reject vague claims such as "predicts the market" until the target and clock
are explicit. Distinguish forecasting a future return from explaining an
initial reaction, nowcasting, imputation, or reconstructing masked data.

### 3. Reconstruct Data And Features

Document universe, assets, sample period, frequency, vendors, filters,
survivorship treatment, missingness, corporate actions, revisions, and entity
mapping.

For every feature family, record:

- economic rationale and expected decay;
- exact transformation and lag;
- point-in-time availability;
- cross-sectional versus time-series information;
- preprocessing, normalization, imputation, selection, and augmentation;
- whether it can encode the label, future universe, or test distribution.

Require feature ablations and compare learned representations with transparent
economic features.

### 4. Audit Splits And Leakage

Require chronological validation. Prefer rolling-origin, expanding-window, or
blocked temporal evaluation plus a final untouched test period.

Check:

- random row, sequence, event, or asset splits that leak neighboring periods;
- overlapping labels requiring purging or embargo;
- scalers, imputers, graph edges, tokenizers, PCA, feature selection, or
  augmentation fit on full data;
- validation or test feedback reused for architecture, prompt, feature, or
  hyperparameter decisions;
- cross-sectional leakage from contemporaneous information unavailable at the
  actual decision time;
- revised fundamentals, survivor universes, post-event text, retrieval, and
  pretrained-model contamination;
- a model or API version that did not exist at the claimed evaluation date.

A test set stops being untouched after the research loop adapts to it.

### 5. Audit Model And Training Choices

Reconstruct architecture, objective, losses, regularization, optimizer,
training budget, hyperparameter search, seeds, early stopping, and model
selection rule.

Demand a reason that the model's inductive bias matches the market problem.
Treat parameter count, context length, pretraining scale, and compute as costs,
not evidence of useful information.

For pretrained or foundation models, audit corpus overlap, cutoff dates,
zero-shot versus adapted evaluation, prompt search, adapters, and whether
"unseen" means unseen series, unseen time, unseen domain, or all three.

### 6. Audit Baselines And Search

Compare under equal information and tuning budgets with:

- naive and seasonal forecasts;
- linear, regularized, and classical time-series models;
- tree-based models;
- simple RNN/CNN/MLP alternatives where relevant;
- simpler portfolio or decision rules.

Count trials across features, architectures, prompts, assets, horizons,
windows, seeds, and reported tables. Treat the selected winner as a
multiple-testing result. Ask whether complexity improves a pre-specified
decision or only one selected benchmark metric.

### 7. Audit Statistical And Economic Evaluation

Match metrics to the target and decision. Report uncertainty, calibration,
cross-sectional and temporal aggregation, regime dispersion, and benchmark
comparisons. Do not let a pooled average hide failure in finance or in
high-value regimes.

For trading claims, reconstruct the complete portfolio rule and report:

- gross and net returns;
- turnover, spreads, market impact, borrow, financing, latency, and capacity;
- beta, factor, sector, volatility, and liquidity exposures;
- drawdowns, tails, concentration, and risk of ruin;
- OOS Sharpe with frequency, annualization, risk-free treatment, overlap, and
  confidence interval stated.

Use `scripts/audit_oos_sharpe.py` when a dated return series is available:

```bash
python scripts/audit_oos_sharpe.py returns.csv \
  --return-column strategy_return \
  --test-start 2024-01-01 \
  --periods-per-year 252
```

The utility recomputes Sharpe on the selected date range and reports a
Newey-West t-statistic, geometric return, drawdown, date-order warnings, and
the absence of an explicit OOS filter. It cannot prove the returns themselves
were generated without leakage.

### 8. Stress Generalization And Deployment

Test or request tests across assets, markets, horizons, eras, volatility
states, crises, structural breaks, seeds, data vendors, model vintages, and
realistic retraining schedules.

Challenge operational assumptions: data and API stability, inference latency,
compute cost, failures, agent permissions, hallucinations, monitoring, model
drift, reproducibility, and rollback. For generative or simulated data,
validate conclusions on untouched real future data.

### 9. Issue The Assessment

Separate:

- what the paper establishes;
- what is only in-sample, generic-domain, or architecture evidence;
- what may result from leakage, search, or weak baselines;
- what survives realistic market implementation;
- the decisive test that could change the verdict.

## Model-Family Diagnostics

### Sequence, Transformer, RNN, And LSTM

- Verify causal masking, window construction, context overlap, and positional
  features.
- Compare useful horizon against context length; long context can memorize
  regimes without generalizing.
- Test simple lag, linear, and recurrent baselines under equal budgets.

### Foundation, Zero-Shot, And Few-Shot Models

- Define pretraining coverage and contamination risk.
- Distinguish zero-shot from prompt selection on the evaluation set.
- Keep adaptation, calibration, and model selection inside training data.
- Require finance-specific performance on genuinely unseen future periods.

### Generative Models

- Audit whether synthetic data preserve tails, dependence, volatility
  clustering, and conditional regimes.
- Train generators without test information.
- Evaluate downstream gains on real untouched data.

### State-Space Models

- Verify causal recurrence and implementation details.
- Treat linear-time scaling as efficiency evidence only.
- Ablate context length and compare SSM, transformer, RNN, and lag baselines.

### Graph And Spatio-Temporal Models

- Construct every graph and relationship point-in-time.
- Test dynamic edges, new entities, missing nodes, and structural breaks.
- Separate graph value from extra parameters and cross-sectional pooling.

### LLMs, Multimodal Models, And Agents

- Timestamp prompts, retrieved documents, model/API versions, and tool output.
- Separate language plausibility from forecast or policy quality.
- Evaluate complete trajectories, tool errors, latency, permissions, and
  realized decisions.

### Explainable AI

- Test explanation faithfulness, stability, and out-of-sample behavior.
- Do not infer causality or tradability from attribution.
- Stress correlated features and economically equivalent representations.

## Output Discipline

When no stricter schema is supplied, return:

1. `domain_fit`: why ML-in-finance expertise is relevant;
2. `claim_and_clock`: central claim, target, horizon, and decision timeline;
3. `data_and_features`: universe, availability, transformations, and risks;
4. `split_and_leakage_audit`: exact protocol and violations or uncertainties;
5. `model_and_search_audit`: architecture rationale, tuning, trials, and
   baselines;
6. `evidence`: source-grounded findings;
7. `economic_evaluation`: implementation and OOS Sharpe assessment;
8. `findings`: strengths and issues ordered by consequence;
9. `decisive_tests`: concrete tests that could change the verdict;
10. `confidence`: confidence and missing evidence.

## Guardrails

- Do not invent data timing, splits, features, tuning, costs, or results.
- Do not call a random split, reused holdout, or post-cutoff evaluation truly
  out of sample.
- Do not treat generic benchmark success as evidence of market predictability.
- Do not treat model complexity, pretraining scale, or interpretability as an
  economic mechanism.
- Do not call forecast accuracy tradable without an executable decision rule
  and net returns.
- Do not accept a headline Sharpe without reconstructing its OOS return series,
  annualization, overlap, costs, and selection process.
- Do not issue investment advice.
