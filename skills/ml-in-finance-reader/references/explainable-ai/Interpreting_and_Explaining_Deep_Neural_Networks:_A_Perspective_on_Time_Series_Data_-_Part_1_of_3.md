# Interpreting and Explaining Deep Neural Networks: A Perspective on Time Series Data - Part 1 of 3: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/explainable-ai/Interpreting_and_Explaining_Deep_Neural_Networks:_A_Perspective_on_Time_Series_Data_-_Part_1_of_3.pdf`  
Document type: research paper  
Topic family: `explainable-ai`  
Extracted text signal: 11,697 characters

## Distillation

This source addresses interpretation and explanation methods for deep models, especially temporal and event-prediction settings.

Source-stated scope and claims:
- In US, 51% of US wages or $2.7 trillion in wages could be automated.
- Uber’s first car accident - Death of Elaine Herzberg Uber's self-driving car killed a pedestrian (Marc 18th, 2018) The ‘safety driver’ was watching a TV show (June 22th, 2018) Do We Understand AI Systems Enough?
- Article Contents EU General Data Protection Regulation (GDPR) Statistically impressive, but individually unreliable Inherent flaws can be exploited Skewed training data creates Maladaptation A DARPA Perspective on AI - Three Waves of AI Explainable AI - Performance vs.
- Properties for Good Attribution Methods: Explanation Continuity  Implementation Invariance • m1 and m2: two functionally equivalent models • For any x, the models produce the same output • An attribution methods is implementation invariant if it always produces identical attributions for m1 and m2.

## Concepts And Methods

- `RNN`
- `explainability`

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
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.

## Source Map

- Results with Perturbation Methods
- methods are equivalent.

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
