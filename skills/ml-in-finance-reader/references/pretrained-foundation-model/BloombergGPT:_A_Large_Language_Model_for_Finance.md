# BloombergGPT: A Large Language Model for Finance: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/BloombergGPT:_A_Large_Language_Model_for_Finance.pdf`  
Document type: research paper  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 203,634 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- Large Language Models (LLMs) have been shown to be effective on a variety of tasks; however, no LLM specialized for the financial domain has been reported in literature.
- In this work, we present BloombergGPT, a 50 billion parameter language model that is trained on a wide range of financial data.
- Our mixed dataset training leads to a model that outperforms existing models on financial tasks by significant margins without sacrificing performance on general LLM benchmarks.
- Additionally, we explain our modeling choices, training process, and evaluation methodology.

## Concepts And Methods

- `zero-shot`
- `few-shot`
- `fine-tuning`
- `pretraining`
- `transformer`
- `GAN`
- `agent`
- `calibration`
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

## Source Map

- 1 Bloomberg, New York, NY USA
- 2 Bloomberg, Toronto, ON Canada
- 3 Computer Science, Johns Hopkins University, Baltimore, MD USA
- 1 Introduction
- 2 Dataset
- 2.1 Financial Datasets (363B tokens - 51.27% of training) . . . . . . . . . . . .
- 2.1.1 Web (298B tokens - 42.01% of training) . . . . . . . . . . . . . . . .
- 2.1.2 News (38B tokens - 5.31% of training) . . . . . . . . . . . . . . . . .
- 2.1.3 Filings (14B tokens - 2.04% of training) . . . . . . . . . . . . . . . .
- 2.1.4 Press (9B tokens - 1.21% of training) . . . . . . . . . . . . . . . . .
- 2.1.5 Bloomberg (5B tokens - 0.70% of training) . . . . . . . . . . . . . .
- 2.2 Public Datasets (345B tokens - 48.73% of training) . . . . . . . . . . . . . .

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
