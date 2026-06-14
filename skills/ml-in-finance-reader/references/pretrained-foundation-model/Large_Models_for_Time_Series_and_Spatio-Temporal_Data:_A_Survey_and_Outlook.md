# Large Models for Time Series and Spatio-Temporal Data: A Survey and Outlook: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/Large_Models_for_Time_Series_and_Spatio-Temporal_Data:_A_Survey_and_Outlook.pdf`  
Document type: survey/review  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 167,737 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- Recent advances in large language models and other foundation models have accelerated their use in time series and spatio-temporal data mining.
- In this survey, we present a comprehensive, up-to-date review of large models tailored or ∗Correspondence to: Shirui Pan <s.pan@griffith.edu.au> and Qingsong Wen <qingsongedu@gmail.com>.
- Overall, this survey consolidates recent advances and highlights foundations, applications, resources, and open research opportunities in large model-centric temporal data analysis.
- Large Models for Time Series and Spatio-Temporal Data: A Survey and Outlook.

## Concepts And Methods

- `zero-shot`
- `few-shot`
- `fine-tuning`
- `pretraining`
- `transformer`
- `RNN`
- `diffusion`
- `GAN`
- `graph neural network`
- `causal inference`

## Finance Reading Lens

Separate broad representation transfer from evidence of market predictability. Audit corpus contamination, model-vintage availability, adaptation leakage, and deployment economics.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Document pretraining coverage, cutoff dates, model version, and evaluation overlap.
- Tune prompts, adapters, normalization, and hyperparameters without consulting final tests.
- Benchmark against strong local statistical and ML models under equal budgets.
- Evaluate genuinely unseen series and regimes; aggregate metrics must not hide finance failure.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 2 Jin et al.
- 1 Introduction
- 4 Jin et al.
- 6 Jin et al.
- 2 Background
- 2.1 Large Language Models
- 2.2 Pre-Trained Foundation Models
- 8 Jin et al.
- 2.3 Time Series and Spatio-Temporal Data
- 3 Overview and Categorization
- 10 Jin et al.
- 4 Large Models for Time Series Data

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
