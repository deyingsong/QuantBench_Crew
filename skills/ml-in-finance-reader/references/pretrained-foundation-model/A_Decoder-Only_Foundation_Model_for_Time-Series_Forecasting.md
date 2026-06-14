# A Decoder-Only Foundation Model for Time-Series Forecasting: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/A_Decoder-Only_Foundation_Model_for_Time-Series_Forecasting.pdf`  
Document type: research paper  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 70,756 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- Motivated by recent advances in large language models for Natural Language Processing (NLP), we design a time-series foundation model for forecasting whose out-of-the-box zero-shot performance on a variety of public datasets comes close to the accuracy of state-of-the-art supervised forecasting models for each individual dataset.
- Our model is based on pretraining a decoder style attention model with input patching, using a large time-series corpus comprising both real-world and synthetic datasets.
- Experiments on a diverse set of previously unseen forecasting datasets suggests that the model can yield accurate zero-shot forecasts across different domains, forecasting horizons and temporal granularities.

## Concepts And Methods

- `zero-shot`
- `fine-tuning`
- `pretraining`
- `transformer`
- `state space model`
- `Mamba`
- `probabilistic forecasting`
- `distribution shift`
- `attention`

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

- 1 Introduction
- 2 Related Work
- 3 Problem Definition
- 4 Model Architecture
- 5 Pretraining Details
- 6 Empirical Results
- 6.1 Zero-shot Evaluation
- 6.2 Ablation
- 7 Conclusion
- 8 Impact Statement
- Results, findings, and conclusions. International Journal of Forecasting, 38(4):1346-1364, 2022.
- results are reported on the last test window of the original test split.

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
