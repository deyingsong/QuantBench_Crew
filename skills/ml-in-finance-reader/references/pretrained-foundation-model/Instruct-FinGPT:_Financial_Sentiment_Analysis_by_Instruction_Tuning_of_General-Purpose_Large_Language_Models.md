# Instruct-FinGPT: Financial Sentiment Analysis by Instruction Tuning of General-Purpose Large Language Models: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/Instruct-FinGPT:_Financial_Sentiment_Analysis_by_Instruction_Tuning_of_General-Purpose_Large_Language_Models.pdf`  
Document type: research paper  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 31,242 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- Despite the impressive capabilities of large language models (LLMs) in financial natural language processing (NLP), they still struggle with accurately interpreting numerical values and grasping financial context, limiting their effectiveness in predicting financial sentiment.
- In this paper, we introduce a simple yet effective instruction tuning approach to address these issues.
- By transforming a small portion of supervised financial sentiment analysis data into instruction data and finetuning a general-purpose LLM with this method, we achieve remarkable advancements in financial sentiment analysis.
- In the experiment, our approach outperforms state-of-the-art supervised sentiment analysis models, as well as widely used LLMs like ChatGPT and LLaMAs, particularly in scenarios where numerical understanding and contextual comprehension are vital.

## Concepts And Methods

- `zero-shot`
- `few-shot`
- `fine-tuning`
- `pretraining`
- `transformer`

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

- 1 Introduction
- 2 Related Work
- 3 Our Method
- 3.1 Instruction Tuning
- 3.2 Comparison Between LLMs and FinBERT for
- 4 Performance Evaluation
- 4.1 Datasets
- 4.2 Model Training
- 4.3 Baseline Models
- results (positive, negative, or neutral) for each text input.
- 4.4 Evaluation and Analysis
- 5 Conclusion and Future Work

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
