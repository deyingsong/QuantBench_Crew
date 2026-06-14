# A Survey on Graph Neural Networks for Time Series: Forecasting, Classification, Imputation, and Anomaly Detection: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/graph-model/A_Survey_on_Graph_Neural_Networks_for_Time_Series:_Forecasting,_Classification,_Imputation,_and_Anomaly_Detection.pdf`  
Document type: survey/review  
Topic family: `graph-model`  
Extracted text signal: 239,569 characters

## Distillation

This source addresses graph neural networks for forecasting, classification, imputation, and anomaly detection in time series.

Source-stated scope and claims:
- These approaches can explicitly model inter-temporal and inter-variable relationships, which traditional and other deep neural network-based methods struggle to do.
- In this survey, we provide a comprehensive review of graph neural networks for time series analysis (GNN4TS), encompassing four fundamental dimensions: forecasting, classification, anomaly detection, and imputation.
- Then, we present and discuss representative research works and introduce mainstream applications of GNN4TS.
- This survey, for the first time, brings together a vast array of knowledge on GNN-based time series research, highlighting foundations, practical applications, and opportunities of graph neural networks for time series analysis.

## Concepts And Methods

- `out-of-sample`
- `pretraining`
- `transformer`
- `RNN`
- `LSTM`
- `diffusion`
- `VAE`
- `GAN`
- `graph neural network`
- `imputation`

## Finance Reading Lens

Treat the graph as a point-in-time feature. Full-sample correlations, future relationships, or hindsight entity links can dominate reported gains.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Build every edge and weight using information available at the prediction date.
- Compare learned graphs with sector, correlation, and no-graph baselines.
- Stress edge turnover, missing nodes, new entities, and regime shifts.
- Separate gains from graph structure versus parameter count and pooling.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- The PDF uses OOS or rolling-evaluation language. Verify the exact split mechanics and whether every preprocessing and tuning choice respects them.
- Finance or market language appears in the PDF. Check whether the finance evidence is a real evaluation domain, an illustrative example, or only motivation.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.
- Uncertainty or probabilistic forecasting appears in the PDF. Check calibration, tail coverage, scoring rules, and usefulness for sizing or risk limits.

## Source Map

- 1 INTRODUCTION
- results [12], [13], [14], [15], [16]. While early research
- application domains nor thoroughly discusses other tasks
- discussion, providing readers with an up-to-date understanding of the state-of-the-art in GNN4TS.
- applications of GNN4TS across various fields, while Sec.
- 2 DEFINITION AND NOTATION
- methods, learning-based approaches aim to learn the graph
- 3 FRAMEWORK AND CATEGORIZATION
- application needs, we categorize this task into two types:
- 3.1 Task-oriented Taxonomy
- methods, such as DiffSTG [55], that share the same objective
- 3.2 Unified Methodological Framework

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
