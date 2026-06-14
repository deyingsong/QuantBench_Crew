# Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/finance-ai/Can_ChatGPT_Forecast_Stock_Price_Movements?_Return_Predictability_and_Large_Language_Models.pdf`  
Document type: research paper  
Topic family: `finance-ai`  
Extracted text signal: 270,421 characters

## Distillation

This source addresses direct applications of language models and multimodal AI to financial forecasting, research, sentiment, or decisions.

Source-stated scope and claims:
- We document the capability of large language models (LLMs) like ChatGPT to predict stock market reactions from news headlines without direct financial training.
- Using postknowledge-cutoff headlines, GPT-4 captures initial market responses, achieving approximately 90% portfolio-day hit rates for the non-tradable initial reaction.
- Forecasting ability generally increases with model size, suggesting that financial reasoning is an emerging capacity of complex LLMs.
- To rationalize these findings, we develop a theoretical model that incorporates LLM technology, information-processing capacity constraints, underreaction, and limits to arbitrage.

## Concepts And Methods

- `out-of-sample`
- `zero-shot`
- `few-shot`
- `fine-tuning`
- `transformer`
- `diffusion`
- `GAN`
- `multimodal`
- `agent`
- `Sharpe ratio`

## Finance Reading Lens

Demand a point-in-time reconstruction of model, prompt, news, market data, retrieval, and execution. A knowledge cutoff alone does not rule out contamination or post-event information.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Timestamp every input, prompt, model version, prediction, and executable trade.
- Separate initial reaction, subsequent drift, and tradable returns.
- Recompute returns after spreads, impact, borrow, delay, and sizing.
- Audit OOS Sharpe, prompt/model multiplicity, regime stability, and adoption decay.
- The PDF discusses Sharpe, a strategy, or portfolio returns. Reconstruct the return series, OOS boundary, annualization, overlap, costs, benchmark exposures, and selection process.
- The PDF uses OOS or rolling-evaluation language. Verify the exact split mechanics and whether every preprocessing and tuning choice respects them.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 Introduction
- 2 Institutional Background
- 3 Conceptual Framework: LLMs, Information Processing, and Market Dynamics
- 3.1 Key Ingredients
- 3.2 LLMs as Information Processors
- 3.3 Mechanism of Predictability
- 3.4 Key Theoretical Insights
- 4 Data
- 5 ChatGPT Prompt
- 6 ChatGPT and Market Information Processing
- 6.1 Can ChatGPT Forecast Stock Price Movements?
- 6.2 Post-Announcement Drift and Predictive Regressions

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
