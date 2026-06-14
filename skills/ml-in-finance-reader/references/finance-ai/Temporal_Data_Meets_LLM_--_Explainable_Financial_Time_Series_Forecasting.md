# Temporal Data Meets LLM - Explainable Financial Time Series Forecasting: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/finance-ai/Temporal_Data_Meets_LLM_--_Explainable_Financial_Time_Series_Forecasting.pdf`  
Document type: research paper  
Topic family: `finance-ai`  
Extracted text signal: 56,505 characters

## Distillation

This source addresses direct applications of language models and multimodal AI to financial forecasting, research, sentiment, or decisions.

Source-stated scope and claims:
- This paper presents a novel study on harnessing Large Language Models’ (LLMs) outstanding knowledge and reasoning abilities for explainable financial time series forecasting.
- In this paper, we focus on NASDAQ-100 stocks, making use of publicly accessible historical stock price data, company metadata, and historical economic/financial news.
- Through the performance comparison results and a few examples, we find LLMs can make a well-thought decision by reasoning over information from both textual news and price time series and extracting insights, leveraging cross-sequence information, and utilizing the inherent knowledge embedded within the LLM.
- Additionally, we show that a publicly available LLM such as Open-LLaMA, after fine-tuning, can comprehend the instruction to generate explainable forecasts and achieve reasonable performance, albeit relatively inferior in comparison to GPT-4.

## Concepts And Methods

- `zero-shot`
- `few-shot`
- `fine-tuning`
- `transformer`
- `RNN`
- `state space model`
- `GAN`
- `graph neural network`
- `multimodal`
- `explainability`

## Finance Reading Lens

Demand a point-in-time reconstruction of model, prompt, news, market data, retrieval, and execution. A knowledge cutoff alone does not rule out contamination or post-event information.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Timestamp every input, prompt, model version, prediction, and executable trade.
- Separate initial reaction, subsequent drift, and tradable returns.
- Recompute returns after spreads, impact, borrow, delay, and sizing.
- Audit OOS Sharpe, prompt/model multiplicity, regime stability, and adoption decay.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 INTRODUCTION
- 2 RELATED WORKS
- 2.1 Traditional Statistical/Econometric
- Methods
- methods for financial time series include Vector Autoregressive
- 2.2 Machine Learning Techniques
- 2.3 Large Language Models
- 3 METHODOLOGY
- 3.1.2 Company Profile Data. We use GTP-4 to generate company
- result of the step-by-step thinking process in response to Figure
- 3.1.3 Finance/Economy News Data. We use Google Custom Search
- 3.2 Instruction-Based Zero-shot/Few-shot

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
