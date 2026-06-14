# Modern Aspects of Big Time Series Forecasting: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/time-series-analysis/Modern_Aspects_of_Big_Time_Series_Forecasting.pdf`  
Document type: lecture/tutorial  
Topic family: `time-series-analysis`  
Extracted text signal: 306,640 characters

## Distillation

This source addresses forecasting, imputation, causality, robustness, augmentation, and nonstationary time-series methodology.

Source-stated scope and claims:
- Algorithms for AWS Services & Open Source: Amazon Forecast, Amazon DevOps Guru, Amazon Lookout for Metrics, Amazon Sagemaker DeepAR, GluonTS, . . .
- 4 Modern approaches (globally finding patterns, deep probabilistic models).
- 5 Forecasting Applications and Tools Q&A and overflow Gasthaus et. al. (Amazon) Modern Forecasting August 19th, 2021 4 / 207 Modern Aspects of Big Time Series Forecasting 1 Introduction to Forecasting 10am - 10:15am.
- 11:55am - 12:15pm 4 Modern approaches (globally finding patterns, deep probabilistic models).

## Concepts And Methods

- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `S4`
- `probabilistic forecasting`
- `calibration`
- `attention`

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

- 1 Introduction to Forecasting
- 2 Classical approaches (local, learning one time series at a time)
- 3 Modern approaches (globally finding patterns). Part 1.
- 4 Modern approaches (globally finding patterns, deep probabilistic models). Part 2.
- 5 Forecasting Applications and Tools
- 1 Introduction to Forecasting 10am - 10:15am.
- 2 Classical approaches (local, learning one time series at a time) 10:15am - 10:45am.
- 3 Modern approaches (globally finding patterns). Part 1. 10:45am - 11:55am
- 5 Forecasting Applications and Tools 1:30pm - 2pm
- Introduction to Forecasting
- 1 Trend features (linear, logarithmic, exponential, logistic, etc.)
- 2 Seasonal features: dummies (one-hot indicators), periodic features (e.g. Fourier, wavelet,

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
