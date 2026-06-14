# Pretraining vs. Finetuning and Modern Transformers (RoPE, GQA, Longformer): ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/Pretraining_vs._Finetuning_+_Modern_Transformers_(RoPE,_GQA,_Longformer).pdf`  
Document type: lecture/tutorial  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 24,086 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- 10-x23 Generative AI Machine Learning Department School of Computer Science Carnegie Mellon University Pretraining vs. finetuning + Modern Transformers (RoPE, GQA, Longformer) Matt Gormley Lecture 4 Jan.
- MNIST digits) • Example B: supervised training on a very large image classification dataset (e.g.
- Input … 12 Unsupervised Autoencoder Pre-Training for Vision Unsupervised pretraining of the first layer: • What should it predict? • What else do we observe? • The input! ’ ’ ’ ’ … “Input” Hidden Layer … This topology defines an Auto-encoder.
- ImageNet w/21k classes and 14M images) Fine-tuning • object detection, training on 200k labeled images from COCO • semantic segmentation, training on 20k labeled images from ADE20k Example: Language Models Pre-training • unsupervised pre-training by maximizing likelihood of a large set of unlabeled sentences s

## Concepts And Methods

- `fine-tuning`
- `pretraining`
- `transformer`
- `RNN`
- `agent`
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
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.

## Source Map

- Section headings were not reliably recoverable from the PDF text layer; navigate using the concepts above.

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
