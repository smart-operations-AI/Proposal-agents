from datetime import datetime
from libs.contracts.models import Outcome, OutcomeStatus
from libs.telemetry.mlflow_tracker import MLflowTracker
from libs.persistence.database import get_engine, OutcomeRecord
from sqlalchemy.orm import sessionmaker

class OutcomeTracker:
    def __init__(self, db_url: str = "sqlite:///./revenue_agents.db"):
        self.engine = get_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.mlflow = MLflowTracker()

    async def record_outcome(self, outcome: Outcome, tenant_id: str):
        # 1. Persist in SQL
        with self.Session() as session:
            record = OutcomeRecord(
                id=f"OUT_{outcome.execution_id}",
                execution_id=outcome.execution_id,
                signal_id=outcome.signal_id,
                tenant_id=tenant_id,
                outcome_status=outcome.outcome_status.value,
                revenue_generated=outcome.revenue_generated,
                revenue_protected=outcome.revenue_protected,
                attribution_confidence=outcome.attribution_confidence,
                time_to_outcome_minutes=outcome.time_to_outcome_minutes
            )
            session.add(record)
            session.commit()

        # 2. Log to MLflow
        self.mlflow.log_outcome(
            execution_id=outcome.execution_id,
            outcome_status=outcome.outcome_status.value,
            revenue=outcome.revenue_generated or outcome.revenue_protected
        )

        print(f"[OutcomeTracker] Recorded {outcome.outcome_status} for execution {outcome.execution_id}")
