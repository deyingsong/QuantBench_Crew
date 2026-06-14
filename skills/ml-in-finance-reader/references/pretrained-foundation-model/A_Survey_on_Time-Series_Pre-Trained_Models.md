# A Survey on Time-Series Pre-Trained Models: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/A_Survey_on_Time-Series_Pre-Trained_Models.pdf`  
Document type: survey/review  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 418,392 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- -Time-Series Mining (TSM) is an important research area since it shows great potential in practical applications.
- Deep learning models that rely on massive labeled data have been utilized for TSM successfully.
- Recently, pre-trained models have gradually attracted attention in the time series domain due to their remarkable performance in computer vision and natural language processing.
- In this survey, we provide a comprehensive review of Time-Series Pre-Trained Models (TS-PTMs), aiming to guide the understanding, applying, and studying TS-PTMs.

## Concepts And Methods

- `zero-shot`
- `few-shot`
- `fine-tuning`
- `pretraining`
- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `Mamba`
- `diffusion`

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

- experiments involving 27 methods, 434 datasets, and 679 transfer
- I. INTRODUCTION
- II. BACKGROUND
- III. OVERVIEW OF TS-PTMS
- 3 L 
- 2 L 
- results on multiple time series datasets demonstrate that TNC
- method based on contrast predictive coding. Particularly, the
- 15 Minimum Target Datasets 15 Medium Target Datasets 15 Maximum Target Datasets
- IV. EXPERIMENTAL RESULTS AND ANALYSIS
- results in Table I. The P-value is calculated for the transfer
- results are shown in Table II. Compared with the supervised

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
