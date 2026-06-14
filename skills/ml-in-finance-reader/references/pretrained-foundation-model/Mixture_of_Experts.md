# Mixture of Experts: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/Mixture_of_Experts.pdf`  
Document type: lecture/tutorial  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 7,006 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- 10-423/10-623 Generative AI Machine Learning Department School of Computer Science Carnegie Mellon University Mixture of Experts Matt Gormley & Pat Virtue Lecture 16 Mar.
- Llama-2 25 Figure from http://arxiv.org/abs/2401.04088 OlMoE Hyperparameters 26 Performance vs.
- Cost MoEs provide a nice tradeoff between performance and FLOPS cost 28 Figure from http://arxiv.org/abs/2409.02060 How many experts to choose?
- Early work with MoEs in LSTM-LMs favored a very large number of experts 29 How many experts to choose?

## Concepts And Methods

- `transformer`
- `RNN`
- `LSTM`
- `multimodal`
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

## Source Map

- 3 Experts: (with same # of total parameters)

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
