# Interpreting and Explaining Deep Neural Networks: A Perspective on Time Series Data - Part 2 of 3: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/explainable-ai/Interpreting_and_Explaining_Deep_Neural_Networks:_A_Perspective_on_Time_Series_Data_-_Part_2_of_3.pdf`  
Document type: research paper  
Topic family: `explainable-ai`  
Extracted text signal: 13,238 characters

## Distillation

This source addresses interpretation and explanation methods for deep models, especially temporal and event-prediction settings.

Source-stated scope and claims:
- Interpreting and Explaining Deep Neural Networks: A Perspective on Time Series Data - Part 2/3 Jaesik Choi Explainable Artificial Intelligence Center Graduate School of Artificial Intelligence KAIST Some slides courtesy of David Bau and M.
- David Bau et. al., 2019 11 GAN Dissection - Do units correlate to an object class?
- David Bau et. al., 2019 12 GAN Dissection - Debugging and Improving GANs David Bau et. al., 2019 13 Is there an erroneous output?
- Pawan Kumar] Neural Networks Verification - Robust Deep Learning Is there an erroneous output?

## Concepts And Methods

- `GAN`

## Finance Reading Lens

Use explanations as diagnostics, not proof of causality or profitability. Test whether explanations are faithful and stable across retraining, folds, regimes, correlated features, and equivalent representations.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Compute explanations only from genuinely out-of-sample predictions.
- Test faithfulness with perturbation or ablation, not visual plausibility alone.
- Audit instability under correlated features, seeds, scaling, and nearby windows.
- Do not turn predictive attribution into a causal or trading claim.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- Experiment : DCGAN-MNIST
- Experiment : PGGAN-LSUN-church
- Experiment : PGGAN-celebA
- Experiment : According to the portion of activate mask

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
