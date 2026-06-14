# Neural Temporal Point Processes: A Review: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/sequence-model/Neural_Temporal_Point_Processes:_A_Review.pdf`  
Document type: survey/review  
Topic family: `sequence-model`  
Extracted text signal: 49,317 characters

## Distillation

This source addresses sequence architectures and temporal point processes for ordered, irregular, or event-time data.

Source-stated scope and claims:
- Temporal point processes (TPP) are probabilistic generative models for continuous-time event sequences.
- Neural TPPs combine the fundamental ideas from point process literature with deep learning approaches, thus enabling construction of flexible and efficient models.
- We conclude this survey with the list of open challenges and important directions for future work in the field of neural TPPs. and machine learning were neural TPPs [Du et al., 2016; Mei and Eisner, 2017].
- The goal of this survey is to provide an overview of neural TPPs, with focus on models (Sections 3-5) and their applications (Section 6).

## Concepts And Methods

- `transformer`
- `RNN`
- `LSTM`
- `diffusion`
- `multimodal`
- `probabilistic forecasting`
- `attention`
- `point process`

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
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 Introduction
- 2 Background and Notation
- 3 Autoregressive Neural TPPs
- 3.1 Representing Events as Feature Vectors
- 3.2 Encoding the History into a Vector
- 3.3 Predicting the Time of the Next Event
- 1 The distribution
- applications is to assume that the TPP is non-terminating,
- 3.4 Modeling the Marks
- 4 Continuous-time State Evolution
- 5 Parameter Estimation
- 5.1 Maximum Likelihood Estimation

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
