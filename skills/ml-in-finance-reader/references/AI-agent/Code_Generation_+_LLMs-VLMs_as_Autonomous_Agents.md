# Code Generation and LLMs-VLMs as Autonomous Agents: ML-in-Finance Reader Distillation

Source PDF: `Source_data/ML_AI/AI-agent/Code_Generation_+_LLMs-VLMs_as_Autonomous_Agents.pdf`  
Document type: lecture/tutorial  
Topic family: `AI-agent`  
Extracted text signal: 20,601 characters

## Distillation

This source addresses LLM/VLM agents, planning, tool use, code generation, and autonomous execution loops.

Source-stated scope and claims:
- 10-x23 Generative AI Machine Learning Department School of Computer Science Carnegie Mellon University Code Generation + LLMs / VLMs as Autonomous Agents Matt Gormley Lecture 23 1 CODE GENERATION 5 How can you boost your productivity as a programmer?
- The build will be validated by rendering a test scene file (/app/deps/illum1.pov) and comparing output against a reference image, with a provided sanity check command to verify the installation works correctly.
- Example: Games chess-best-move: Analyze a chess position from an image file to determine and output the optimal move(s) for white.
- The solution must identify the best move(s) from the given board state and write them to a file in algebraic notation format (source square followed by destination square, e.g., e2e4).

## Concepts And Methods

- `transformer`
- `agent`
- `attention`

## Finance Reading Lens

Treat an agent as a controlled decision-and-execution system. Separate answer quality from policy quality, tool correctness, permissions, reproducibility, and realized economic outcomes.

The transfer to markets is not established by architecture novelty or generic benchmark performance alone. Require a point-in-time information set, chronological evaluation, strong simple baselines, and decision-relevant economics.

## Source-Specific Audit Questions

- Freeze the information set at every agent step; retrieval and tool results can leak future facts.
- Evaluate complete trajectories and execution outcomes, not only final-answer style.
- Sandbox code, data, and trading tools; require logs, approvals, and rollback paths.
- Measure hallucination, compounding error, latency, and cost under market-time constraints.
- The PDF does not clearly center trading performance. Do not manufacture a Sharpe or tradability claim from its generic forecasting results.
- OOS or rolling-evaluation language was not clearly detected. Treat finance generalization as unproven until a chronological protocol is supplied.
- Implementation or code language appears in the PDF. Audit the actual code path for causal masking, preprocessing leakage, defaults, seeds, and evaluation mismatches.

## Source Map

- Applications for Code Models
- evaluation
- results, logs, or tool outputs.

## Use And Limits

- Use this reference to route attention and formulate tests; verify decisive claims in the original PDF, tables, appendices, and code.
- Separate source-stated claims from the finance-reader audit questions above.
- Do not infer causality, tradability, or robust OOS Sharpe from forecast accuracy alone.
