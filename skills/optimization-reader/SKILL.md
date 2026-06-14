---
name: optimization-reader
description: Read and review optimization methods used in portfolio construction, portfolio management, and other financial decisions as a domain expert, covering linear, quadratic, conic, nonlinear, mixed-integer, stochastic, dynamic, robust, distributionally robust, multi-objective, and machine-learning-assisted optimization; input estimation, constraints, solver diagnostics, uncertainty, transaction costs, rebalancing, backtesting, and scalability. Use when Scout detects a paper whose central contribution or evidence depends on formulating, solving, or validating a financial optimization problem; invoke from Reader for source-grounded extraction and from Reviewer for adversarial mathematical, computational, and economic critique.
---

# Optimization Reader

Analyze optimization research as a complete decision system connecting an
economic objective, information set, variables, constraints, uncertainty,
mathematical formulation, solver, and realized outcome. Do not call a solution
useful because it is optimal for a model; verify that the model represents the
financial decision and that the computed solution is reliable.

## Routing

Treat a paper as in-domain when its central contribution depends on one or more
of:

- portfolio construction, allocation, rebalancing, tracking, or risk budgeting;
- linear, quadratic, conic, nonlinear, fractional, semidefinite, or
  mixed-integer financial optimization;
- stochastic, dynamic, robust, or distributionally robust optimization;
- chance constraints, scenario optimization, uncertainty sets, or
  multi-objective decisions;
- solver methods, decomposition, heuristics, relaxations, or scalability for a
  finance problem;
- optimization in execution, hedging, asset-liability management, derivatives,
  capital allocation, balance-sheet management, or other financial domains.

Do not route a paper merely because it runs an optimizer as a routine final
step. The formulation, algorithm, uncertainty treatment, constraints, solver,
or resulting decision must be central.

When a paper's central contribution is primarily options, microstructure,
factors, or macro/rates, combine this skill with the corresponding domain
reader. When invoked by Reader, reconstruct the method faithfully before
criticizing it. When invoked by Reviewer, challenge the result using the paper,
run artifacts, and optimization diagnostics. Preserve the caller's requested
schema.

## Reference Router

Load only the references needed for the task:

- For practical mean-variance extensions, estimation error, constraint costs,
  alpha-risk alignment, Black-Litterman, risk parity, multiple alpha sources,
  and multi-period portfolios, read
  [60-years-portfolio-optimization.md](references/60-years-portfolio-optimization.md).
- For modern input estimation, convex risk measures, conic and mixed-integer
  formulations, risk parity, robust methods, clustering and graph portfolios,
  synthetic scenarios, and multi-asset backtesting, read
  [advanced-portfolio-optimization.md](references/advanced-portfolio-optimization.md).
- For LP-computable criteria, transaction costs, lots, thresholds,
  cardinality, logical dependencies, tracking, heuristics, and computational
  testing, read
  [linear-and-mixed-integer-programming.md](references/linear-and-mixed-integer-programming.md).
- For robust estimation, stochastic and dynamic programming, uncertainty sets,
  robust counterparts, solvers, model risk, rebalancing, and transaction costs,
  read
  [robust-portfolio-optimization-and-management.md](references/robust-portfolio-optimization-and-management.md).

Read multiple references when a conclusion connects formulation validity,
uncertainty modeling, numerical solution, and implementable finance outcomes.

## Workflow

### 1. Establish Evidence And Decision Scope

Record the paper, appendices, code, data, solver logs, parameter files,
experiments, and run artifacts. Label missing evidence. Separate explicit paper
statements from inference.

Identify the decision-maker, information time, decision horizon, instruments,
current state, action, objective, and operational consequences. State what the
optimizer is intended to improve relative to a named baseline.

### 2. Reconstruct The Economic Problem

Extract:

- decision variables, domains, units, and timing;
- objective terms and economic interpretation;
- constraints and their institutional or financial rationale;
- uncertain parameters and information available at decision time;
- current holdings, state variables, trades, and terminal conditions;
- risk, return, cost, utility, or liability definitions.

Distinguish targets, trades, and realized positions. For multi-objective models,
identify scalarization, lexicographic priority, Pareto criterion, or constraint
conversion and explain how preference parameters are chosen.

### 3. Classify The Mathematical Formulation

Determine whether the problem is:

- LP, QP, QCQP, SOCP, SDP, or another convex program;
- fractional, nonlinear, or nonconvex;
- mixed-integer linear, convex, or nonlinear;
- stochastic, chance-constrained, dynamic, robust, or distributionally robust;
- bilevel, equilibrium, game-theoretic, or heuristic.

Verify that the classification matches the actual objective and constraints.
Identify transformations, auxiliary variables, relaxations, approximations,
decomposition, and reformulations.

### 4. Audit Mathematical Validity

Check dimensions, units, variable bounds, signs, domains, feasibility,
boundedness, and constraint consistency. Verify that covariance matrices and
other required matrices have the necessary properties.

For claimed convex programs, verify convexity and disciplined formulation
rules. For transformations, prove or test equivalence and recovery of the
original variables. For relaxations and approximations, state what guarantees
are lost and how approximation error is measured.

Use duality, KKT conditions, shadow prices, limiting cases, or small
independently solved examples when appropriate.

### 5. Audit Inputs, Estimation, And Alignment

Inspect how expected returns, risks, transition dynamics, costs, scenarios,
and other coefficients are estimated. Record data timing, window, shrinkage,
factor model, distributional assumption, forecast error, and regime
dependence.

Challenge whether:

- the optimization amplifies estimation error;
- alpha, risk, cost, and constraint models are aligned;
- parameters are estimated at the same horizon as the decision;
- missing risks appear free to the optimizer;
- point estimates are treated as certain without justification;
- model selection and tuning leak future information.

### 6. Audit Constraints And Financial Realism

Map each constraint to a financial rule or operational need. Distinguish hard
requirements from discretionary regularization. Quantify binding constraints,
shadow costs, and interactions where possible.

Audit position and exposure bounds, leverage, funding, shorting, borrow,
turnover, liquidity, taxes, lots, minimum holdings, cardinality, logical
dependencies, tracking, capital, and regulatory requirements.

Do not assume that more constraints make a model more realistic. Contradictory,
poorly calibrated, or excessively tight constraints can determine the solution
and conceal weak forecasts.

### 7. Audit Solver And Numerical Evidence

Record solver, version, algorithm, formulation passed to the solver, scaling,
tolerances, initialization, warm starts, random seeds, hardware, time and
memory limits, and termination status.

For convex problems, verify primal and dual feasibility, objective residuals,
and optimality status. For nonconvex problems, identify local versus global
claims and initialization sensitivity. For mixed-integer problems, require the
incumbent, best bound, absolute and relative optimality gaps, and time-limit
effects.

Review Big-M validity, relaxation strength, numerical conditioning, scenario
size, decomposition, and heuristic reproducibility. A feasible solution is not
necessarily an optimal solution.

### 8. Audit Uncertainty And Dynamics

Distinguish uncertainty semantics:

- stochastic models require scenarios and probabilities;
- robust models require uncertainty sets and protection levels;
- distributionally robust models require ambiguity sets over distributions;
- dynamic models require states, controls, transitions, and terminal values.

Audit scenario generation, probability calibration, nonanticipativity,
scenario reduction, state sufficiency, time consistency, uncertainty-set
geometry, radius calibration, robust-counterpart derivation, and conservatism.

Require sensitivity across uncertainty assumptions. Do not treat worst-case
protection, average-case performance, and probabilistic guarantees as
interchangeable.

### 9. Audit Implementation And Portfolio Translation

For portfolio problems, begin from current holdings and translate optimal
variables into executable trades. Include turnover, spread, impact, taxes,
borrow, financing, incomplete execution, and rebalancing frequency.

For other finance domains, identify the analogous implementation layer:
hedge instruments and rebalances, execution and fills, funding and collateral,
capital usage, operational limits, or policy actions.

Evaluate whether the optimizer's target remains feasible and beneficial after
implementation. Separate mathematical objective value from realized economic
value.

### 10. Validate, Compare, And Issue The Assessment

Compare against simple rules, current practice, continuous relaxations,
alternative formulations, and appropriate domain baselines. Use chronological
walk-forward tests, stress scenarios, parameter perturbations, ablations,
regime splits, and scalability experiments.

Report stability of decisions, objective values, realized outcomes, costs,
constraint violations, run time, and optimality gaps. Separate:

- what is mathematically established;
- what is computationally demonstrated;
- what depends on inputs, uncertainty, or solver assumptions;
- what improves realized financial decisions;
- which decisive test could change the conclusion.

## Domain Diagnostics

### Convex And Continuous Models

- Is convexity established and the reformulation equivalent?
- Are feasibility, dual residuals, and KKT or optimality evidence available?
- Does regularization improve out-of-sample decisions rather than only smooth
  weights?

### Nonconvex And Mixed-Integer Models

- Is a global optimum claimed without a certificate?
- Are Big-M values and variable bounds valid and tight?
- What are the relaxation gap, incumbent quality, and time-limit sensitivity?
- Does integrality add economic value relative to the continuous relaxation?

### Stochastic, Dynamic, And Robust Models

- Do scenarios preserve decision-relevant dependence and tails?
- Are nonanticipativity, state transitions, and time consistency correct?
- Are uncertainty or ambiguity sets calibrated and economically interpretable?
- Does protection justify conservatism and computational cost?

### Portfolio Construction And Management

- Are alpha, risk, costs, constraints, and horizon aligned?
- Which constraints bind and consume utility?
- Does the portfolio survive estimation error, turnover, costs, and
  rebalancing?
- Does complexity beat simple allocations out of sample?

### Other Financial Domains

- Does the optimization capture the domain's contracts, market mechanics,
  institutional rules, and implementation path?
- Are domain-specific state variables and constraints omitted?
- Should another domain-reader skill be invoked for the decisive critique?

## Output Discipline

When no stricter caller schema is supplied, return:

1. `domain_fit`: why the optimization expert was invoked;
2. `decision_and_economic_objective`: decision-maker, variables, objective,
   horizon, and baseline;
3. `formulation`: mathematical class, constraints, transformations, and
   uncertainty semantics;
4. `inputs_and_assumptions`: estimation, data timing, dynamics, and alignment;
5. `solver_and_computational_evidence`: status, tolerances, gaps, scaling, and
   reproducibility;
6. `domain_findings`: strengths and issues ordered by consequence;
7. `implementation_validation_and_decisive_tests`: realized economics,
   generalization, and tests that could change the verdict;
8. `confidence`: confidence and missing evidence.

## Guardrails

- Do not invent objectives, variables, constraints, parameters, solver
  settings, or guarantees.
- Do not call a solution globally optimal without an appropriate certificate.
- Do not equate solver success status with economic validity.
- Do not accept a reformulation, relaxation, or approximation without checking
  equivalence or stated error.
- Do not call a model robust without explicit uncertainty semantics and
  calibrated protection.
- Do not let in-sample objective improvement outrank out-of-sample realized
  outcomes, stability, costs, and constraint violations.
- Do not compare methods without aligning data, horizons, constraints, and
  implementation assumptions.
- Do not let added complexity outrank simple defensible baselines.
- Do not issue investment advice.
