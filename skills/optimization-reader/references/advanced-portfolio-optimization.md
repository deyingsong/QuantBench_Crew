# Advanced Portfolio Optimization

## Source

Dany Cajas, *Advanced Portfolio Optimization: A Cutting-edge Quantitative
Approach* (Springer Nature Switzerland, 2025).

## Contents

- [Why This Source Matters](#why-this-source-matters)
- [Input Estimation](#input-estimation)
- [Convex Modeling And Risk Measures](#convex-modeling-and-risk-measures)
- [Objectives And Real Features](#objectives-and-real-features)
- [Mixed-Integer Formulations](#mixed-integer-formulations)
- [Risk Parity](#risk-parity)
- [Robust And Stochastic Optimization](#robust-and-stochastic-optimization)
- [Machine-Learning And Graph Portfolios](#machine-learning-and-graph-portfolios)
- [Backtesting](#backtesting)
- [Optimization-Reader Diagnostics](#optimization-reader-diagnostics)

## Why This Source Matters

This book treats portfolio optimization as a sequential process:

1. estimate input parameters;
2. select and solve an optimization model;
3. backtest the resulting investment strategy.

It provides a broad modern taxonomy spanning convex risk measures, conic and
mixed-integer formulations, risk parity, robust optimization, clustering,
graphs, synthetic scenarios, and multi-asset backtesting. Use it to review
whether a proposed optimizer is formulated correctly, solved appropriately,
and validated as a complete decision process.

## Input Estimation

The source covers sample moments, exponentially weighted estimates,
multivariate time-series models, shrinkage, random-matrix denoising,
graph-based covariance methods, explicit and implicit factor models, and
Black-Litterman variants.

The optimizer's apparent sophistication cannot compensate for poor inputs.
Review:

- estimation window and weighting;
- positive-semidefinite covariance handling;
- shrinkage target and intensity;
- factor selection and loading stability;
- denoising and detoning choices;
- view construction and confidence;
- sensitivity to alternative estimators.

Parameter estimation, model selection, and backtesting must use only
information available at each decision date.

## Convex Modeling And Risk Measures

Convex optimization is attractive because, under appropriate conditions, a
global optimum can be found efficiently. The source uses disciplined convex
programming and conic representations to model a wide range of objectives and
risk measures.

Covered risk families include dispersion, downside, range, drawdown, higher
moments, coherent, spectral, distortion, and ordered-weighted-average
measures. CVaR can be represented as a linear program under scenarios.

Reviewers should ask:

- Does the chosen risk measure match the economic loss of concern?
- Is the claimed formulation truly convex?
- Are transformations and auxiliary variables equivalent to the original
  problem?
- Does the solver support the required cones and numerical tolerances?
- Are tail and drawdown estimates supported by enough data?

## Objectives And Real Features

Return-risk formulations can minimize risk, maximize return, maximize utility,
or maximize a risk-adjusted ratio. These are not interchangeable unless the
assumptions and transformations establish equivalence.

Real-feature constraints include linear exposure limits, index tracking,
convex features, and mixed-integer restrictions. Audit all constraints in the
same units as the variables and confirm that the feasible set is nonempty.

## Mixed-Integer Formulations

Binary variables can represent semi-continuous holdings, indicators,
cardinality, mutually exclusive positive and negative positions, and exact
absolute-value relationships.

Mixed-integer models require special scrutiny:

- Big-M values must be valid and reasonably tight.
- Binary variables must activate the intended decisions.
- Bounds must reflect actual investment limits.
- Solver status, incumbent objective, best bound, and optimality gap matter.
- Time limits and heuristics can return feasible but non-optimal portfolios.

Do not compare a mixed-integer result with a continuous model without
separating the value of the economic constraint from the cost of integrality.

## Risk Parity

Risk parity can allocate risk across assets or factors and can use different
risk measures. Risk contribution definitions must satisfy the required
decomposition assumptions. Equal risk contribution does not imply equal
capital allocation or economic diversification.

Review whether:

- asset or factor risk is being equalized;
- the risk measure admits the claimed contribution decomposition;
- leverage and return requirements are explicit;
- the result is a true risk-parity solution or an approximation;
- risk concentration persists in correlated groups.

## Robust And Stochastic Optimization

The source covers resampling, stochastic optimization, chance constraints,
worst-case optimization with box and elliptical uncertainty sets, and
near-optimal centering.

Resampling can smooth weights and increase diversification, but remains
sensitive to the data-generating inputs and can be computationally expensive.

Scenario-based chance constraints may require mixed-integer formulations.
Distributional assumptions can make them cheaper to solve, but transfer model
risk into the assumed distribution.

Worst-case models require explicit uncertainty sets and parameters. Audit how
sets are estimated, whether the implied conservatism is economically sensible,
and whether the robust counterpart is derived correctly.

## Machine-Learning And Graph Portfolios

Hierarchical risk parity, hierarchical equal-risk contribution, nested
clustered optimization, and graph-based constraints use estimated dependence
structures to shape allocations.

These methods do not eliminate estimation risk. Results can change with
distance measure, linkage method, cluster count, graph filter, and covariance
window. Validate cluster and graph stability, compare with simple baselines,
and do not infer causality from a dendrogram or network.

## Backtesting

Backtesting should simulate a live multi-asset process. The source covers
walk-forward evaluation, cross-validation, combinatorial purged
cross-validation, historical and synthetic scenarios, rolling and expanding
windows, rebalancing rules, benchmarks, and transaction costs.

Require:

- chronological, point-in-time parameter estimation;
- explicit rebalance and holding rules;
- transaction costs, fees, and slippage;
- no leakage between train and test periods;
- multiple regimes and synthetic stress scenarios;
- stability of weights, risk, turnover, and performance;
- comparison against simple allocations and alternative optimizers.

## Optimization-Reader Diagnostics

- Is the model convex, conic, fractional, or mixed-integer as claimed?
- Are solver status, tolerances, gaps, and scaling disclosed?
- Do input estimators and risk measures match the decision horizon?
- Are uncertainty and scenario models independently validated?
- Are machine-learning structures stable?
- Does walk-forward net performance justify complexity?

## Source-Led Review Standard

Review the entire pipeline, not only the mathematical program. An optimization
method is credible only when its inputs are point-in-time, its formulation is
equivalent to the economic problem, its solver output is diagnosed, and its
portfolio behavior survives realistic out-of-sample backtesting.
