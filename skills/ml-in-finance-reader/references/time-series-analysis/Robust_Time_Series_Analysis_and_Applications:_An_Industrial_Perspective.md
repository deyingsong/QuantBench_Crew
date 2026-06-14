# Robust Time Series Analysis and Applications: An Industrial Perspective: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/time-series-analysis/Robust_Time_Series_Analysis_and_Applications:_An_Industrial_Perspective.pdf`  
Document type: lecture/tutorial  
Topic family: `time-series-analysis`  
Extracted text signal: 54,270 characters

## Distillation

This source addresses forecasting, imputation, causality, robustness, augmentation, and nonstationary time-series methodology.

Source-stated scope and claims:
- KDD 2022 Tutorial Robust Time Series Analysis and Applications: An Industrial Perspective •Date and Time: Aug.
- Gaussian ● When assumptions not hold linear Gaussian Model misspecification Outliers ● Robust regression ○ Robust regression methods are designed to be not overly affected by violations of assumptions by the underlying data-generating process.
- 16/103 Majorization-Minimization (MM) Algorithms ● Consider the problem difficult to optimize directly ● Surrogate function Easy to optimize ● Convergence guarantee Sun, Ying, Prabhu Babu, and Daniel P.
- Palomar. "Majorization-minimization algorithms in signal processing, communications, and machine learning." IEEE Transactions on Signal Processing 65.3 (2016): 794-816.

## Concepts And Methods

- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `augmentation`
- `explainability`
- `probabilistic forecasting`
- `attention`
- `wavelet transform`

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

- Applications of Time Series in Industry
- applications
- Experiments on Real-World Data
- Application of RobustDTW: Time Series Outlier Detection
- Application of RobustDTW: Periodicity Detection

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
