# Architecture Overview: Revenue MoE Platform

## 1. Vision
The platform is designed to convert predictive signals (churn, upsell, risk) into automated, revenue-protecting actions using a **Mixture of Experts (MoE)** multi-agent system. It balances specialized intelligence with parallel execution and strict governance.

## 2. Core Components

### MoE Intelligence Layer
- **Router Agent**: Calculates semantic affinity between signals and expert profiles using local embeddings. Implements Top-k gating and load balancing.
- **Experts**:
    - **FIA (Financial)**: ROI optimization and pricing strategy.
    - **SEA (Sales)**: Outreach strategy and messaging optimization.
    - **Risk**: Assessment of payment defaults and collateral requirements.
    - **Escalation**: High-value/complex review logic.
- **Aggregator**: Merges expert outputs using weighted fusion (Softmax) for numeric params and priority-based selection for categorical ones.

### Execution & Communication
- **Workflow Engine (LangGraph)**: Manages state transitions with **parallel execution** via Send objects.
- **Agent Message Bus**: Asynchronous Pub/Sub bus for lateral communication (e.g., Risk Expert querying FIA for advice).
- **SEA Execution Agent**: Implements actions via CRM/ERP adapters using Dependency Injection (contextvars).

### Infrastructure Layer
- **Local Inference**: Offline execution using **Ollama** (Chat) and **SentenceTransformers** (Embeddings).
- **Persistence**: Multi-tenant SQL (PostgreSQL) with async connection pooling and Redis for telemetry.
- **Memory**: ChromaDB for RAG-based context retrieval.

## 3. Data Flow
1. **Ingest & Normalize**: Predictions are converted into `InternalSignals`.
2. **Route**: The Router selects `k` experts based on semantic affinity and current system load.
3. **Parallel Expert Execution**: Selected experts run concurrently, communicating via the Message Bus.
4. **Aggregate**: Outputs are merged into a single `RevenueCommand`.
5. **Guardrail & Execute**: Policies are validated, and SEA executes the command via adapters.
6. **Track**: Metrics and outcomes are persisted for load balancing and performance analysis.

## 4. Key Design Principles
- **Parallel MoE**: Experts run concurrently for reduced latency and specialized accuracy.
- **Offline First**: Zero dependency on external LLM APIs.
- **Lateral Communication**: Agents collaborate in real-time to resolve dependencies.
- **Resilience**: Dedicated error-handling nodes and async persistent checkpointing.
