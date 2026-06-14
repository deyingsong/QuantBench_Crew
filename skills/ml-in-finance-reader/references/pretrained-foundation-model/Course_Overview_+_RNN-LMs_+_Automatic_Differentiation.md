# Course Overview and RNN-LMs and Automatic Differentiation: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/Course_Overview_+_RNN-LMs_+_Automatic_Differentiation.pdf`  
Document type: survey/review  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 49,735 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- 10-x23 Generative AI Machine Learning Department School of Computer Science Carnegie Mellon University Course Overview + RNN-LMs + Automatic Differentiation Matt Gormley & Aran Nayebi Lecture 1 1 WHAT IS GENERATIVE AI?
- 5 Artificial Intelligence The basic goal of AI is to develop intelligent machines.
- This consists of many sub-goals: • Perception • Reasoning • Control / Motion / Manipulation • Planning • Communication • Creativity • Learning Artificial Intelligence Machine Learning Deep Learning GenAI 6 Artificial Intelligence The basic goal of AI is to develop intelligent machines.
- 14 Artificial Intelligence The basic goal of AI is to develop intelligent machines.

## Concepts And Methods

- `zero-shot`
- `fine-tuning`
- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `Mamba`
- `diffusion`
- `VAE`
- `GAN`

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

- 651 Gb
- 325 Gb
- methods in real-world
- application
- 15 J=ce_layer.apply_fwd(y,
- method
- BACKGROUND:

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
