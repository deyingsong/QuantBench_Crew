# Generative Adversarial Networks for Spatio-Temporal Data: A Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/generative-model/Generative_Adversarial_Networks_for_Spatio-Temporal_Data:_A_Survey.pdf`  
Document type: survey/review  
Topic family: `generative-model`  
Extracted text signal: 103,998 characters

## Distillation

This source addresses GANs, VAEs, diffusion models, and related generative or representation-learning architectures.

Source-stated scope and claims:
- 1 Generative Adversarial Networks for Spatio-Temporal Data: A Survey arXiv:2008.08903v4 [cs.LG] 30 Jul 2021 NAN GAO, HAO XUE, WEI SHAO, SICHEN ZHAO, KYLE KAI QIN, ARIAN PRABOWO, MOHAMMAD SAIEDUR RAHAMAN, and FLORA D.
- SALIM, RMIT University, Australia Generative Adversarial Networks (GANs) have shown remarkable success in producing realistic-looking images in the computer vision area.
- In this paper, we have conducted a comprehensive review of the recent developments of GANs for spatio-temporal data.
- Generative Adversarial Networks for Spatio-Temporal Data: A Survey.

## Concepts And Methods

- `RNN`
- `LSTM`
- `S4`
- `VAE`
- `GAN`
- `imputation`
- `multimodal`
- `agent`
- `probabilistic forecasting`
- `attention`

## Finance Reading Lens

Judge generated data by economically relevant joint and conditional distributions, tails, temporal dependence, and regimes, not appearance alone.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Fit preprocessing and generators on training windows only.
- Compare real and synthetic tails, autocorrelation, cross-asset dependence, and volatility clustering.
- Validate downstream models on untouched real future data.
- Test augmentation gains across seeds, windows, and regimes.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 INTRODUCTION
- methods use deterministic models (e.g., RNN) and cannot capture the stochastic behaviour of
- evaluation metrics for GAN on ST data [40, 138].
- methods for modelling ST data. A taxonomy of the different types of ST data instances has been
- 2 PRELIMINARY
- 2.1 Spatio-temporal Data
- 2.1.1 Properties. There are several general properties for ST data (i.e., spatial reference, time
- 2.1.2 Data Types. There are various spatio-temporal data types in real-world applications, differing
- 2.2 Spatio-Temporal Deep Learning with Non-GAN Networks
- 2.2.1 CNN. Convolutional Neural Network (CNN) [81] is a type of deep, feed-forward neural
- 2.2.2 RNN, LSTM and GRU. Recurrent Neural Network (RNN) [109] is a type of neural networks
- 2.2.3 Autoencoder (AE). AE [66] is a neural network that is trained to copy its input to its output

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
