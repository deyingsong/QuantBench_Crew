# Real-world Issues and Considerations: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/pretrained-foundation-model/Real-world_Issues_and_Considerations.pdf`  
Document type: lecture/tutorial  
Topic family: `pretrained-foundation-model`  
Extracted text signal: 8,625 characters

## Distillation

This source addresses pretraining, foundation models, transfer, in-context learning, multimodality, and efficient adaptation.

Source-stated scope and claims:
- 10-423/623/723: Generative AI Lecture 22 - Real-world Issues and Considerations Aran Nayebi & Matt Gormley Slide Credit: Henry Chai 10-423/623/723: Generative AI Lecture 22 - What can go wrong?
- What does it mean (in the context of generative AI)?
- 11 A (Tiny) Subset of Risks Associated with Generative AI  Copyright infringement  Susceptibility to adversarial attack  Hallucinations  Bias/discrimination  Generation of toxic/unsafe content  Environmental impact  We’ll examine these using the following framework: 1.
- 10/21/24 68 Source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator#results Environmental Impacts of Training Large Generative Models Source: https://dl.acm.org/doi/pdf/10.1145/3531146.3533234 69 Those are some pretty large error bars (note the logscale!), what’s causing that?

## Concepts And Methods

- `fine-tuning`
- `transformer`
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

- Section headings were not reliably recoverable from the PDF text layer; navigate using the concepts above.

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
