# Linear And Mixed Integer Programming For Portfolio Optimization

## Source

Renata Mansini, Włodzimierz Ogryczak, and M. Grazia Speranza, *Linear and
Mixed Integer Programming for Portfolio Optimization* (Springer, 2015).

## Contents

- [Source Limitation](#source-limitation)
- [Why This Source Matters](#why-this-source-matters)
- [Recoverable Source Map](#recoverable-source-map)
- [Linear-Programming Lens](#linear-programming-lens)
- [Mixed-Integer Lens](#mixed-integer-lens)
- [Transaction Costs And Rebalancing](#transaction-costs-and-rebalancing)
- [Computational Review](#computational-review)
- [Optimization-Reader Diagnostics](#optimization-reader-diagnostics)

## Source Limitation

The attached PDF has a damaged cross-reference structure. PDFKit reports 131
pages, but most body text is not extractable or visible; Ghostscript cannot
recover its page tree. The detailed embedded outline is readable and reliably
identifies the source's topics and section structure.

This note therefore distills the source conservatively from that recoverable
outline. Consult a repaired or replacement copy before citing detailed
formulas, propositions, empirical results, or author-specific conclusions.

## Why This Source Matters

The recoverable structure centers on linear and mixed-integer portfolio models
that represent real investment features directly. It is particularly relevant
when a paper claims practical realism through transaction costs, lots,
thresholds, cardinality, logical dependencies, rebalancing, or index tracking.

The source's organization also emphasizes theoretical consistency, scalable
solution methods, data issues, and model comparison. These are essential
checks whenever discrete portfolio restrictions make the problem materially
harder than its continuous relaxation.

## Recoverable Source Map

The embedded outline identifies seven main areas:

1. portfolio optimization foundations;
2. linear models for portfolio optimization;
3. portfolio optimization with transaction costs;
4. other real portfolio features;
5. rebalancing and index tracking;
6. theoretical framework;
7. computational issues.

The linear-model section covers scenarios and LP computability, LP-computable
risk and safety measures, relationships among risk, safety, and ratio
measures, and advanced LP-computable measures.

The real-features sections explicitly identify:

- transaction-cost structure and complete cost-aware models;
- transaction lots;
- investment thresholds;
- cardinality constraints;
- logical or decision-dependency constraints;
- portfolio rebalancing;
- index and enhanced-index tracking;
- long-short portfolios.

The theoretical and computational sections identify stochastic dominance,
coherent measures, linear and mixed-integer solvers, a kernel-search
heuristic, data issues, large-scale LP models, and model testing and
comparison.

## Linear-Programming Lens

Scenario-based portfolio objectives and risk measures may admit linear
representations through auxiliary variables. A linear formulation can be
highly scalable, but only if it is equivalent to the intended economic
criterion.

Review:

- scenario construction and probabilities;
- the exact risk, safety, or ratio measure;
- linearization and auxiliary-variable logic;
- units and normalization;
- whether the LP objective captures the relevant tail or downside behavior;
- whether stochastic-dominance or coherence claims actually hold.

## Mixed-Integer Lens

Real portfolio rules often require binary or integer variables. Typical
questions prompted by the source's recoverable structure are:

- Do lots reflect executable quantities?
- Do minimum investment thresholds apply only when an asset is selected?
- Does cardinality count holdings or trades?
- Are logical dependencies and exclusions encoded correctly?
- Are long and short selections treated consistently?
- Does the formulation allow accidental simultaneous or contradictory states?

Every integer restriction should have an economic reason. Discrete realism can
improve implementability while sharply increasing computational difficulty.

## Transaction Costs And Rebalancing

Cost-aware optimization should distinguish current holdings, trades, and final
holdings. Costs may be fixed, variable, piecewise, or triggered only when a
trade occurs. Fixed costs and thresholds commonly require integer decisions.

For rebalancing and tracking problems, inspect:

- target benchmark and tracking measure;
- current portfolio and transition trades;
- turnover, fixed costs, and lots;
- enhanced-index alpha objective;
- long-short and funding constraints;
- trade-off between tracking quality and implementation cost.

## Computational Review

Mixed-integer programs can be computationally demanding. Solver output must
distinguish proven optimality from a feasible incumbent.

Require:

- solver and version;
- formulation size and preprocessing;
- time and memory limits;
- incumbent objective and best bound;
- relative and absolute optimality gaps;
- numerical tolerances;
- heuristic use and reproducibility;
- scalability tests as universe and scenario counts grow.

Kernel-search or other heuristics may improve tractability, but a heuristic
solution is not a proof of global optimality. Compare it with bounds,
relaxations, and exact solutions on smaller cases.

## Optimization-Reader Diagnostics

- Is the LP or MIP formulation economically faithful?
- Which constraints truly require integrality?
- Is the continuous relaxation informative and tight?
- Are transaction costs, lots, thresholds, and dependencies represented on
  trades or holdings correctly?
- Does the solver prove optimality or stop with a gap?
- Are large-scale results stable across data, scenarios, and solver settings?
- Are models compared on both objective value and implementable outcomes?

## Source-Led Review Standard

Treat discrete constraints as part of the economic model, not decorative
realism. Verify their logic, quantify their cost, inspect relaxation strength
and solver gaps, and demand reproducible evidence that the resulting portfolio
is both feasible and materially better suited to the real decision.
