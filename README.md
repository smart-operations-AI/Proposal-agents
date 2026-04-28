# Revenue Automation Agents

Platform for multi-agent revenue automation protocols using FIA (Financial Intelligence Agent) and SEA (Sales Execution Agent).

## Architecture (MoE Multi-Agent)

- **Router Agent**: Dynamic signal routing using top-k gating and load-balance awareness.
- **Expert Layer**: Specialized autonomous agents (FIA, SEA, Risk, Escalation) with private memory.
- **Aggregator**: Weighted result merging for unified command generation.
- **Guardrails**: Real-time policy validation and persistent idempotency.

## Stack

- **Python 3.11+**
- **LangGraph**: Workflow orchestration (Conditional MoE Graph).
- **MLflow**: Decision and outcome tracking.
- **PostgreSQL**: Multi-tenant persistent storage.
- **ChromaDB**: Private agent memory (RAG).
- **SQLAlchemy**: Database abstraction layer.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Run the sample worker:
   ```bash
   $env:PYTHONPATH="."
   python apps/worker/main.py
   ```

3. Run the API Gateway:
   ```bash
   $env:PYTHONPATH="."
   uvicorn services.model_gateway.api:api --reload
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Repository Structure

- `services/`: Core logic services (FIA, SEA, Workflow).
- `libs/`: Shared libraries (Contracts, Adapters, Telemetry).
- `apps/`: Entry points (API, Workers).
- `infra/`: Deployment configurations.
