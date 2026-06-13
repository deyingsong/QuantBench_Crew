---
name: coder-source-grounding
description: Ground every strategy-implementation decision in the extracted spec and the paper, not in memory, convention, or a plausible default. Use when implementing a candidate strategy module, when a signal/construction detail could be done several ways, or when you are tempted to fill an implementation choice from habit instead of from the MethodSpec, EmpiricalSpec, or the paper itself.
---

# Coder Source Grounding

Adapted for the QuantBench Coder from agent-skills
[source-driven-development](../engineering/skills/source-driven-development/SKILL.md).
There, the source of truth is official framework documentation. Here it is the
**paper and its extracted specs** — the `MethodSpec`, `EmpiricalSpec`, and
their `evidence` links — plus the in-repo contract docs
([quant-coder](../quant-coder/SKILL.md)). An implementation choice that cannot
be traced to one of those is a guess.

## Overview

A faithful reproduction is one whose every performance-affecting choice traces
to the source. Habit and "how strategies are usually coded" are exactly how a
reproduction drifts from the paper it claims to reproduce.

## When to Use

- Implementing or revising any candidate strategy module.
- A signal, construction, window, or sample choice has several plausible forms.
- You are about to write a default value you did not read in the spec.

## The Process

### 1. Detect the contract and tier

Confirm the data surface (`PanelData` API) and the sandbox tier (stdlib-only vs
numeric) you are targeting, exactly as [quant-coder](../quant-coder/SKILL.md)
defines them. Implementing against the wrong tier is the analog of coding to
the wrong framework version.

### 2. Fetch the spec, not your memory

Read the `MethodSpec` and `EmpiricalSpec` fields that govern the choice, and
their `evidence` links into the paper. If the source is silent or vague, do not
fill from convention — route the gap to
[consult-reader](../consult-reader/SKILL.md).

### 3. Implement following the documented method

Write the simplest implementation that matches the sourced definition. Where
the paper and a "nicer" implementation disagree, the paper wins.

### 4. Cite the source

For each non-obvious choice, leave a brief comment naming the spec field or
paper location it rests on (e.g. `# 6-1 momentum, skip last month — MethodSpec.signal_definition`).
A choice with no citable source is a flag to revisit, not to ship.

## Red Flags

- A window length, weighting, or sample boundary that appears in the code but
  not in the spec or paper.
- "This is the standard way" as the justification for a performance-affecting
  choice.
- Filling a vague field from habit instead of consulting the Reader.

## Verification

- [ ] Every performance-affecting choice traces to a spec field or paper location.
- [ ] The implementation targets the correct sandbox tier and data contract.
- [ ] Gaps were routed to consult-reader, not filled by convention.
