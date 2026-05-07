# Technical Documentation: Revenue MoE Engine

This document provides a deep dive into the implementation details of the Revenue MoE (Mixture of Experts) system.

## 1. Local Inference Engine
The system uses `LocalInferenceEngine` to abstract interactions with local LLMs and embedding models.

- **LLM Integration**: Uses Ollama's `/api/chat` endpoint. This provides better structured output and system/user role separation. 
- **Concurrency**: LLM calls are handled via `httpx.AsyncClient`.
- **Embeddings**: Uses `sentence-transformers`. To prevent blocking the Python event loop (as model inference is CPU/GPU intensive), the `encode` method is executed in a thread pool using `asyncio.run_in_executor`.

## 2. MoE Orchestration (LangGraph)
The core workflow is a directed graph where nodes represent agent actions or processing steps.

### Parallelism (Send API)
The Router node determines which experts should handle a specific signal. Instead of linear execution, the system uses LangGraph's `Send` objects to trigger multiple expert nodes in parallel.

### State Reduction
When experts run in parallel, they return results concurrently. The `AgentState` uses a **Reducer** (`operator.add`) on the `expert_outputs` field to automatically merge lists of results from different branches without data loss.

### Error Handling
Each expert node is wrapped in a try-except block. If an error occurs:
1. The error message is appended to the `errors` list in the state.
2. A conditional edge detects the presence of errors and routes the workflow to the `handle_error` node instead of the `aggregator`.

## 3. Communication Bus
The `AgentMessageBus` provides a lateral communication channel (Pub/Sub) between agents.

- **Use Case**: A `Risk Expert` might publish a `risk_query` topic. A `FIA Expert` (Financial) can subscribe to this topic to provide real-time economic context to the risk assessment.
- **Implementation**: Fully asynchronous with a thread-safe subscriber registry.

## 4. Persistence & Guardrails
- **PostgreSQL**: Used for long-term storage of signals, commands, and outcomes. Utilizes `AsyncPostgresSaver` for graph checkpointing, ensuring auditability and recovery.
- **Idempotency**: A dedicated manager checks if a similar action has been executed for a specific client within a configurable window (default 7 days) using async SQLAlchemy queries.
- **Redis**: Stores real-time metrics such as expert utilization and load balancing scores to inform routing decisions.

## 5. Dependency Injection
To ensure testability and modularity, the system uses `contextvars` for injecting adapters (CRM, ERP, Messaging) into the execution nodes. This allows swapping real infrastructure for mocks during testing or development without modifying the core business logic.
