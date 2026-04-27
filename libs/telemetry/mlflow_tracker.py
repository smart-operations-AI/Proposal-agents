import mlflow
from typing import Any, Dict

class MLflowTracker:
    def __init__(self, experiment_name: str = "Revenue_Automation"):
        mlflow.set_experiment(experiment_name)

    def log_decision(self, tenant_id: str, signal_id: str, decision: str, metrics: Dict[str, float]):
        with mlflow.start_run(run_name=f"Decision_{signal_id}"):
            mlflow.set_tag("tenant_id", tenant_id)
            mlflow.set_tag("signal_id", signal_id)
            mlflow.set_tag("decision", decision)
            mlflow.log_metrics(metrics)

    def log_outcome(self, execution_id: str, outcome_status: str, revenue: float):
        # Find active run or start new one? Usually linked by signal_id
        with mlflow.start_run(run_name=f"Outcome_{execution_id}"):
            mlflow.set_tag("execution_id", execution_id)
            mlflow.set_tag("status", outcome_status)
            mlflow.log_metric("revenue", revenue)
