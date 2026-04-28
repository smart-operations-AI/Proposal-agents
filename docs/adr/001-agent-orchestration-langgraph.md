# ADR 001: Orchestration Engine Selection (LangGraph)

## Status
Accepted

## Context
We need a framework to orchestrate complex interactions between agents (FIA, SEA) and external services (Policy Engine). The workflow requires state management, cycles (retries), and conditional branching (escalation/guardrails).

## Decision
We have selected **LangGraph** for orchestration.

## Rationale
- **State Persistence**: LangGraph provides native support for check-pointing and state persistence across agent steps.
- **Cycles and Loops**: Unlike linear DAG engines, LangGraph allows for cycles, which are essential for retries and feedback loops.
- **Multi-Agent Flow**: It provides a clear way to define nodes (agents) and edges (transitions), making the protocol easier to visualize and audit.
- **Human-in-the-loop**: Built-in support for breakpoints facilitates human escalation.

## Consequences
- **Positive**: High flexibility for complex agentic protocols and built-in observability.
- **Negative**: Increased learning curve compared to simple linear scripts.
- **Dependency**: We are dependent on the LangChain/LangGraph ecosystem.
