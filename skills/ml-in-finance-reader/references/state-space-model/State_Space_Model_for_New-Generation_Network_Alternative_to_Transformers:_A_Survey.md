# State Space Model for New-Generation Network Alternative to Transformers: A Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/state-space-model/State_Space_Model_for_New-Generation_Network_Alternative_to_Transformers:_A_Survey.pdf`  
Document type: survey/review  
Topic family: `state-space-model`  
Extracted text signal: 165,808 characters

## Distillation

This source addresses structured state-space models, S4/Mamba selective SSMs, hybrids, and efficient long-sequence computation.

Source-stated scope and claims:
- -In the post-deep learning era, the Transformer architecture has demonstrated its powerful performance across pre-trained big models and various downstream tasks.
- Among them, the State Space Model (SSM), as a possible replacement for the self-attention based Transformer model, has drawn more and more attention in recent years.
- In this paper, we give the first comprehensive review of these works and also provide experimental comparisons and analysis to better demonstrate the features and advantages of SSM.
- Then, we propose possible research points in this direction to better promote the development of the theoretical model and application of SSM.

## Concepts And Methods

- `zero-shot`
- `fine-tuning`
- `pretraining`
- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `Mamba`
- `S4`
- `diffusion`

## Finance Reading Lens

Long-context efficiency is an engineering advantage, not evidence that distant market history is stable or useful. Identify which horizons and states improve future decisions.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Verify causal implementations; bidirectional operations and normalization can expose the future.
- Compare equal-budget SSM, transformer, RNN, linear, and lag baselines.
- Ablate context length and test rolling regime changes.
- Report compute, latency, memory, and robustness with forecast metrics.
- The PDF discusses Sharpe, a strategy, or portfolio returns. Reconstruct the return series, OOS boundary, annualization, overlap, costs, benchmark exposures, and selection process.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 INTRODUCTION
- experiments on multiple downstream tasks to validate the
- 2 FORMULATION OF SSM
- 3 STATE SPACE MODEL
- 3.1 Origin and Variation of SSM
- 1 Gu et al. [34] NeurIPS21 Origin - LSSL Classification
- 2 HiPPO [36] NeurIPS20 Origin - - Classification (pMNIST)acc: 98.34 Speed: 470,000
- 3 S4 [29] ICLR22 Origin 249M DPLR Classification
- 4 S4D [37] arXiv22 Origin - Diagonal - (LRA)avg: 86.09 - -
- 5 DSS [38] NeurIPS22 Origin - SSM Classification
- 6 LRU [39] ICML23 Origin - RNNs, SSM Classification
- 7 S4-LegS [40] ICLR23 Origin 150K S4, Math Classification

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
