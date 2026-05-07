# Revenue Automation Agents (Edge Arena)

A production-ready, multi-agent Mixture of Experts (MoE) platform for revenue operations automation. Designed for high-performance, local-first intelligence using LangGraph, Ollama, and asynchronous infrastructure.

## 🚀 Key Features

- **Autonomous MoE Architecture**: Dynamic routing of signals to specialized experts (Financial, Sales, Risk) with weighted consensus aggregation.
- **Local-First Intelligence**: Real-time inference using **Ollama (Llama 3)** and **SentenceTransformers** for semantic processing without external API dependencies.
- **Parallel Execution**: Highly concurrent workflow orchestration using **LangGraph's parallel node execution** (Send API).
- **Asynchronous Resilience**: Fully async persistence (PostgreSQL + asyncpg), real-time telemetry (Redis), and dedicated error-handling nodes.
- **Multi-Agent Collaboration**: Lateral communication between agents via a custom asynchronous **Message Bus**.

## 🏗️ Technical Stack

- **Orchestration**: LangGraph (v0.2+)
- **LLM Engine**: Ollama (Chat API)
- **Embeddings**: SentenceTransformers (Local execution)
- **Database**: PostgreSQL (Async SQLAlchemy + asyncpg)
- **Cache/Metrics**: Redis (Async)
- **Memory**: ChromaDB (Vector Search / RAG)
- **Validation**: Pydantic v2

## 🛠️ Setup & Execution

### Prerequisites
- Python 3.11+
- Ollama installed and running (`ollama serve`)
- PostgreSQL and Redis instances

### Installation
```bash
# Clone the repository
git clone https://github.com/smart-operations-AI/Dataizen_agents
cd Dataizen_agents

# Install dependencies
pip install -e .
```

### Running the System
```bash
# Set PYTHONPATH
$env:PYTHONPATH="."

# Launch the revenue worker
python apps/worker/main.py

# Launch the API Gateway
uvicorn services.model_gateway.api:api --host 0.0.0.0 --port 8000
```

## 🧪 Testing
```bash
# Run all tests
pytest

# Run integration tests specifically
pytest tests/integration/test_full_workflow.py
```

## 📂 Project Structure
- `apps/`: Worker and API entry points.
- `services/`: Specialized agent nodes and workflow logic.
- `libs/`: Shared core (ML engines, message bus, persistence, guardrails).
- `docs/`: Technical architecture and ADRs.
- `tests/`: Unit, integration, and E2E test suites.

## 📖 Documentation
- [Architecture Overview](docs/architecture/overview.md)
- [Technical Details](docs/architecture/technical_details.md)
