import os

directories = [
    "services/model_gateway",
    "services/signal_normalizer",
    "services/fia_service",
    "services/policy_engine",
    "services/priority_engine",
    "services/sea_service",
    "services/workflow_engine",
    "services/outcome_tracker",
    "services/escalation_service",
    "services/partner_feedback_export",
    "libs/contracts",
    "libs/telemetry",
    "libs/ml",
    "libs/memory",
    "libs/orchestration",
    "libs/tenants",
    "libs/adapters",
    "libs/guardrails",
    "apps/api",
    "apps/worker",
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "infra/docker",
    "infra/k8s",
    "docs/architecture",
    "docs/adr",
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    # Create an empty __init__.py in each directory to make it a package
    if not directory.startswith(("infra", "docs")):
        with open(os.path.join(directory, "__init__.py"), "w") as f:
            pass

print("Project structure initialized successfully.")
