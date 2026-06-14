# Physics-Guided AI for Large-Scale Spatiotemporal Data: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/spatio-temporal-model/Physics-Guided_AI_for_Large-Scale_Spatiotemporal_Data.pdf`  
Document type: survey/review  
Topic family: `spatio-temporal-model`  
Extracted text signal: 80,150 characters

## Distillation

This source addresses joint modeling of temporal dynamics and spatial, relational, or event structure.

Source-stated scope and claims:
- Spatiotemporal Events Irregular space, irregular time: data collected at changing locations and uneven time intervals.
- Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations.
- Integrating physics-based modeling with machine learning: A survey. arXiv preprint arXiv:2003.04919.
- AI Models • Physics Rules and Equations High Contain knowledge gaps in describing certain processes (turbulence, groundwater flow) Use of Scientific Theory Theory-based Models Physics-based Models Theory-guided Data Science Models • Computati

## Concepts And Methods

- `pretraining`
- `transformer`
- `RNN`
- `LSTM`
- `state space model`
- `S4`
- `diffusion`
- `GAN`
- `imputation`
- `calibration`

## Finance Reading Lens

Translate space into a defensible point-in-time market relationship, then verify gains survive structural change and do not encode future outcomes.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Define relations point-in-time and document their update schedule.
- Use temporal tests with structural breaks and unseen entities.
- Compare temporal-only and relation-only ablations.
- Do not import physical invariance into adaptive markets without testing it.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- Methods
- Limitations of Physics-based Models
- methods without ignoring the
- 1 Karpatne et al. “Theory-guided data science: A new
- Methods,” CRC Press, to appear in Spring
- methods used for
- Applications:
- Conclusion: Neural networks will first learn the target
- 6 Practical insights
- Method
- 4.4 Reaction-diffusion dynamics in a two-dimensional Gray-Scott model
- evaluation criterion, going beyond standard

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
