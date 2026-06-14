# Time-Series Forecasting with Deep Learning: A Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/time-series-analysis/Time-Series_Forecasting_with_Deep_Learning:_A_Survey.pdf`  
Document type: survey/review  
Topic family: `time-series-analysis`  
Extracted text signal: 53,785 characters

## Distillation

This source addresses forecasting, imputation, causality, robustness, augmentation, and nonstationary time-series methodology.

Source-stated scope and claims:
- Time-seriesforecastingwith deeplearning:asurvey royalsocietypublishing.org/journal/rsta BryanLimandStefanZohren Review Citethisarticle:Lim,B,ZohrenS.2021 Time-seriesforecastingwithdeeplearning:a survey.Phil.
- A 379:20200209. https://doi.org/10.1098/rsta.2020.0209 Accepted:28July2020 Oxford-ManInstituteforQuantitativeFinance,Departmentof EngineeringScience,UniversityofOxford,Oxford,UK SZ,0000-0002-3392-0394 Numerous deep learning architectures have been developed to accommodate the diversity of timeseries datasets across different domains.
- SubjectAreas: artificialintelligence,statistics Keywords: deepneuralnetworks,time-seriesforecasting, uncertaintyestimation,hybridmodels, interpretability,counterfactualprediction in hybrid deep learning models, which combine well-studied statistical models with neural network components to improve pure methods in either category.
- While we focus on univariate forecasting in this survey (i.e.

## Concepts And Methods

- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `S4`
- `diffusion`
- `GAN`
- `causal inference`
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

- applications in topics such as climate modelling [1],
- methods-as shown in figure 2 and described in detail below.
- limitations, demonstrating improved performance over pure statistical or machine learning
- 2014 Learning phrase representations using RNN Encoder-Decoder for statistical machine
- 2017 Attention is all you need. In Advances in Neural Information Processing Systems (NIPS),
- methods: further empirical evidence. Int. J. Forecast. 14, 339-358. (doi:10.1016/S0169-2070

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
