# Transformers in Time Series: A Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/sequence-model/Transformers_in_Time_Series:_A_Survey.pdf`  
Document type: survey/review  
Topic family: `sequence-model`  
Extracted text signal: 53,605 characters

## Distillation

This source addresses sequence architectures and temporal point processes for ordered, irregular, or event-time data.

Source-stated scope and claims:
- Transformers have achieved superior performances in many tasks in natural language processing and computer vision, which also triggered great interest in the time series community.
- Among multiple advantages of Transformers, the ability to capture long-range dependencies and interactions is especially attractive for time series modeling, leading to exciting progress in various time series applications.
- In this paper, we systematically review Transformer schemes for time series modeling by highlighting their strengths as well as limitations.
- In particular, we examine the development of time series Transformers in two perspectives.

## Concepts And Methods

- `few-shot`
- `pretraining`
- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `VAE`
- `GAN`
- `graph neural network`
- `augmentation`

## Finance Reading Lens

Match the model to the market clock. Distinguish event-intensity prediction from directional return prediction and account for censoring, asynchrony, and latency.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Preserve event order; random event splits leak neighboring history.
- Model market hours, censoring, simultaneous events, and timestamp resolution.
- Connect likelihood or accuracy gains to calibrated decisions and economics.
- Test whether complexity beats recency, seasonality, and Hawkes-style baselines.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 Introduction
- applications [Han et al., 2021], CV applications [Han et al.,
- 2 Preliminaries of the Transformer
- 2.1 Vanilla Transformer
- 2.2 Input Encoding and Positional Encoding
- 2.3 Multi-head Attention
- Application
- 2.4 Feed-forward and Residual Network
- 3 Taxonomy of Transformers in Time Series
- 4 Network Modifications for Time Series
- 4.1 Positional Encoding
- 4.2 Attention Module

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
