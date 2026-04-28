# Revenue Automation Agents

Platform for multi-agent revenue automation protocols using FIA (Financial Intelligence Agent) and SEA (Sales Execution Agent).

## Architecture

- **Intelligence Layer**: Model gateway and signal normalization using PySpark.
- **Execution Layer**: Agent orchestration using LangGraph.
- **Infrastructure Layer**: Multi-tenant persistence (SQLAlchemy) and semantic memory (ChromaDB).

## Stack

- **Python 3.11+**
- **LangGraph**: Workflow orchestration.
- **MLflow**: Model and decision tracking.
- **PySpark**: Data processing and normalization.
- **PyTorch**: Predictive model inference.
- **ChromaDB**: Policy retrieval (RAG).
- **SQLAlchemy**: Multi-tenant database.

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
