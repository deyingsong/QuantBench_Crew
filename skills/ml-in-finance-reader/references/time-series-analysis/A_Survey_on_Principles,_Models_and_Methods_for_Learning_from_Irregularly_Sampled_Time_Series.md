# A Survey on Principles, Models and Methods for Learning from Irregularly Sampled Time Series: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/time-series-analysis/A_Survey_on_Principles,_Models_and_Methods_for_Learning_from_Irregularly_Sampled_Time_Series.pdf`  
Document type: survey/review  
Topic family: `time-series-analysis`  
Extracted text signal: 123,464 characters

## Distillation

This source addresses forecasting, imputation, causality, robustness, augmentation, and nonstationary time-series methodology.

Source-stated scope and claims:
- Irregularly sampled time series data arise naturally in many application domains including biology, ecology, climate science, astronomy, and health.
- Such data represent fundamental challenges to many classical models from machine learning and statistics due to the presence of non-uniform intervals between observations.
- However, there has been significant progress within the machine learning community over the last decade on developing specialized models and architectures for learning from irregularly sampled univariate and multivariate time series data.
- We then survey the recent literature organized primarily along the axis of modeling primitives.

## Concepts And Methods

- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `VAE`
- `GAN`
- `imputation`
- `irregular sampling`
- `agent`
- `calibration`

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

- methods in terms of three key properties including the underlying data representation they
- methods with diﬀerent capabilities and limitations.
- 2.1 Series-Based Representation
- 2.2 Vector-Based Representation
- results in the need to represent missing data. Following Little and Rubin (2014), the
- 2.3 Set-Based Representation
- 4.1 Discretization
- 4.2 Interpolation
- 4.2.1 Similarity
- 4.3 Recurrence
- 4.4 Attention
- 4.5 Structural Invariance

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
