# Architecture Overview: Revenue Automation Platform

## 1. Vision
The platform is designed to convert predictive signals (churn, upsell, risk) into automated, revenue-protecting actions using a multi-agent system. It balances autonomy with strict governance (guardrails) and multi-tenant isolation.

## 2. Core Components

### Intelligence Layer
- **Model Gateway**: FastAPI entry point for external predictions.
- **Signal Normalizer**: PySpark-based data cleaning and enrichment.
- **FIA (Financial Intelligence Agent)**: The "Brain". Calculates economic impact (ROI) and prioritizes actions.

### Execution Layer
- **Workflow Engine**: Orchestrated by **LangGraph**. Manages the state machine and agent transitions.
- **Policy Engine**: Centralized business rules and guardrails.
- **SEA (Sales Execution Agent)**: The "Hands". Executes actions via CRM, ERP, and Messaging adapters.

### Infrastructure Layer
- **Persistence**: Multi-tenant SQL database (SQLAlchemy).
- **Memory**: Semantic Vector Store (ChromaDB) for RAG-based policy retrieval.
- **Telemetry**: MLflow for tracking decisions, experiments, and business outcomes.

## 3. Data Flow
1. **Ingest**: Predictions arrive at the Gateway.
2. **Normalize**: Data is cleaned and converted into `InternalSignals`.
3. **Decide**: FIA ranks signals and creates a `RevenueCommand` with a rationale.
4. **Validate**: Policy Engine checks constraints (margins, caps) and issues a `validation_token`.
5. **Execute**: SEA verifies the token and interacts with SAP (ERP) or Salesforce (CRM).
6. **Track**: Outcomes are recorded in MLflow for performance analysis.

## 4. Key Design Principles
- **Multi-tenancy**: Strictly isolated at the DB and memory level.
- **Idempotency**: Prevents duplicate actions within signal validity windows.
- **Auditability**: Every decision is justified and logged with a trace ID.
