# Time Series Data Augmentation for Deep Learning: A Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/time-series-analysis/Time_Series_Data_Augmentation_for_Deep_Learning:_A_Survey.pdf`  
Document type: survey/review  
Topic family: `time-series-analysis`  
Extracted text signal: 48,066 characters

## Distillation

This source addresses forecasting, imputation, causality, robustness, augmentation, and nonstationary time-series methodology.

Source-stated scope and claims:
- Deep learning performs remarkably well on many time series analysis tasks recently.
- As an effective way to enhance the size and quality of the training data, data augmentation is crucial to the successful application of deep learning models on time series data.
- In this paper, we systematically review different data augmentation methods for time series.
- We propose a taxonomy for the reviewed methods, and then provide a structured review for these methods by highlighting their strengths and limitations.

## Concepts And Methods

- `transformer`
- `RNN`
- `LSTM`
- `VAE`
- `GAN`
- `imputation`
- `augmentation`
- `multimodal`
- `probabilistic forecasting`
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

- 1 Introduction
- applications, such as AlexNet [Krizhevsky et al., 2012] for
- methods for time series data. Firstly, the intrinsic properties
- methods can be designed and implemented in the transformed
- methods systematically. We start the discussion from the simTime Series
- Methods
- methods, model-based methods, and learning-based methods.
- 2 Basic Data Augmentation Methods
- 2.1 Time Domain
- method is introduced in [Fawaz et al., 2018]. This method
- 2.2 Frequency Domain
- experiments of [Gao et al., 2020].

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
