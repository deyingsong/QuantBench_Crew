# Deep Learning for Spatio-Temporal Data Mining: A Survey: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/spatio-temporal-model/Deep_Learning_for_Spatio-Temporal_Data_Mining:_A_Survey.pdf`  
Document type: survey/review  
Topic family: `spatio-temporal-model`  
Extracted text signal: 134,754 characters

## Distillation

This source addresses joint modeling of temporal dynamics and spatial, relational, or event structure.

Source-stated scope and claims:
- -With the fast development of various positioning techniques such as Global Position System (GPS), mobile devices and remote sensing, spatio-temporal data has become increasingly available nowadays.
- In this paper, we provide a comprehensive survey on recent progress in applying deep learning techniques for STDM.
- We first categorize the types of spatio-temporal data and briefly introduce the popular deep learning models that are used in STDM.
- Next we classify existing literatures based on the types of ST data, the data mining tasks, and the deep learning models, followed by the applications of deep learning for STDM in different domains including transportation, climate science, human mobility, location based social network, crime analysis, and neuroscience.

## Concepts And Methods

- `RNN`
- `LSTM`
- `diffusion`
- `VAE`
- `GAN`
- `graph neural network`
- `imputation`
- `multimodal`
- `attention`

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

## Source Map

- I. INTRODUCTION
- methods, the advantages of deep learning models for STDM
- application domains, by making it possible to see how deep
- II. CATEGORIZATION OF SPATIO-TEMPORAL DATA
- applications. Different application scenarios and ST data types
- III. FRAMEWORK
- IV. DEEP LEARNING MODELS FOR ADDRESSING
- application of deep neural networks to precipitation estimation
- V. APPLICATIONS
- application. To better meet customers’ demand and improve
- Application domains Related works
- VI. OPEN PROBLEMS

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
