# Deep Learning for Time Series Forecasting: Tutorial and Literature Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/time-series-analysis/Deep_Learning_for_Time_Series_Forecasting:_Tutorial_and_Literature_Survey.pdf`  
Document type: survey/review  
Topic family: `time-series-analysis`  
Extracted text signal: 138,818 characters

## Distillation

This source addresses forecasting, imputation, causality, robustness, augmentation, and nonstationary time-series methodology.

Source-stated scope and claims:
- Deep learning based forecasting methods have become the methods of choice in many applications of time series prediction or forecasting often outperforming other approaches.
- Consequently, over the last years, these methods are now ubiquitous in large-scale industrial forecasting applications and have consistently ranked among the best entries in forecasting competitions (e.g., M4 and M5).
- This practical success has further increased the academic interest to understand and improve deep forecasting methods.
- In this article we provide an introduction and overview of the field: We present important building blocks for deep forecasting in some depth; using these building blocks, we then survey the breadth of the recent deep forecasting literature.

## Concepts And Methods

- `zero-shot`
- `few-shot`
- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `diffusion`
- `GAN`
- `graph neural network`
- `multimodal`

## Finance Reading Lens

Use this material as the methodological backbone: define the information set, preserve chronology, benchmark simply, and separate statistical accuracy from economic value.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Use rolling-origin, expanding-window, or blocked temporal evaluation.
- Fit transforms, scalers, imputers, selection, and augmentation inside training folds.
- Compare naive, linear, classical, and strong ML baselines.
- Evaluate uncertainty, calibration, regime stability, and a final untouched period.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 Introduction
- 2 Deep Forecasting: A Tutorial
- 2.1 Notation and Formalization of the Forecasting Problem
- 2.2 Neural Network Architectures
- 2.2.1 Multilayer perceptron
- 2.2.2 Convolutional neural networks
- 2.2.3 Recurrent neural networks
- 2.2.4 Transformer
- 2.3 Input Transformations
- 2.4 Output Models and Loss Functions
- 2.4.1 PDF
- 2.4.2 Quantile function

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
