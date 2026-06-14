# The Wall Street Neophyte: A Zero-Shot Analysis of ChatGPT Over Multimodal Stock Movement Prediction Challenges: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/finance-ai/The_Wall_Street_Neophyte:_A_Zero-Shot_Analysis_of_ChatGPT_Over_Multimodal_Stock_Movement_Prediction_Challenges.pdf`  
Document type: research paper  
Topic family: `finance-ai`  
Extracted text signal: 43,754 characters

## Distillation

This source addresses direct applications of language models and multimodal AI to financial forecasting, research, sentiment, or decisions.

Source-stated scope and claims:
- Recently, large language models (LLMs) like ChatGPT have demonstrated remarkable performance across a variety of natural language processing tasks.
- In this paper, we conduct an extensive zero-shot analysis of ChatGPT’s capabilities in multimodal stock movement prediction, on three tweets and historical stock price datasets.
- Our findings indicate that ChatGPT is a "Wall Street Neophyte" with limited success in predicting stock movements, as it underperforms not only state-of-the-art methods but also traditional methods like linear regression using price features.
- This research provides insights into ChatGPT’s capabilities and serves as a foundation for future work aimed at improving financial market analysis and prediction by leveraging social media sentiment and historical stock data.

## Concepts And Methods

- `zero-shot`
- `fine-tuning`
- `transformer`
- `RNN`
- `LSTM`
- `VAE`
- `GAN`
- `multimodal`
- `explainability`
- `agent`

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

## Source Map

- 1 Introduction
- 2 Methodology
- 2.1 Task
- 2.2 Datasets
- 2.3 Prompts
- 2.3.1 Zero-shot prompt
- 2.3.2 Chain of Thought Enhanced Zero-shot Prompt
- 2.4 Baselines
- methods, we consider following approaches:
- 2.5 Metrics
- 3 Experiments
- 3.1 Implementation Details

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
