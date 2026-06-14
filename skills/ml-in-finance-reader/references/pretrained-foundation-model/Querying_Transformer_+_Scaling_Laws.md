# Querying Transformer and Scaling Laws: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/Querying_Transformer_+_Scaling_Laws.pdf`  
Document type: lecture/tutorial  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 10,815 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- Vision Transformers appeared in 2021 Question: Why did it take so long for transformers to become popular in computer vision?
- Vision Transformers appeared in 2021 2017 2020 Vision Transformer Dall-E 2009 PascalVOC AlexNet 2010 VAEs DDPM 2021 2012 VGG Timeline: Image Generation 2013 2014 R-CNN GANs CLIP 2015 2022 Diffusion models ResNet Dall-E 2 Imagen Stable diffusion 2023 SDXL SDXL Turbo 15 How large are LLMs?
- Comparison of some recent large language models (LLMs) Model Creators Year of release Training Data (# tokens) Model Size (# parameters) GPT-2 OpenAI 2019 ~10 billion (40Gb) 1.5 billion GPT-3 (cf.
- ChatGPT) OpenAI 2020 300 billion 175 billion PaLM Google 2022 780 billion 540 billion Chinchilla DeepMind 2022 1.4 trillion 70 billion LaMDA (cf.

## Concepts And Methods

- `transformer`
- `RNN`
- `diffusion`
- `VAE`
- `GAN`
- `multimodal`

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

- Section headings were not reliably recoverable from the PDF text layer; navigate using the concepts above.

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
