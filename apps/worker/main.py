import asyncio
from datetime import datetime
from libs.contracts.models import InputPayload, PredictionEntry
from services.workflow_engine.graph import app
from libs.persistence.database import init_db, get_engine

async def run_sample():
    # 0. Initialize DB and Seed Config
    engine = get_engine()
    init_db(engine)
    
    from libs.tenants.config import TenantConfigService
    config_service = TenantConfigService()
    config_service.update_config("tenant_001", {
        "min_margin_pct": 12.0,
        "max_discount_pct": 10.0,
        "standard_execution_cost": 25.0,
        "strategic_accounts": ["STRAT_999"],
        "preferred_channel": "WHATSAPP"
    })
    # 1. Prepare Mock Payload
    sample_payload = InputPayload(
        tenant_id="tenant_001",
        batch_id="batch_001",
        model_version="churn_v3",
        predictions=[
            PredictionEntry(
                client_id="cl_001",
                model_type="churn",
                score=0.84,
                predicted_value="high_risk",
                prediction_timestamp=datetime.now(),
                validity_window_hours=72,
                recommended_priority=91
            ),
            PredictionEntry(
                client_id="STRAT_999", # Strategic Account
                model_type="upsell",
                score=0.95,
                predicted_value="high_potential",
                prediction_timestamp=datetime.now(),
                validity_window_hours=24,
                recommended_priority=99
            )
        ]
    )

    # 2. Initialize State
    initial_state = {
        "tenant_id": "tenant_001",
        "trace_id": f"trace_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "input_payload": sample_payload,
        "signals": [],
        "current_signal": None,
        "active_command": None,
        "is_blocked": False,
        "blocking_reason": None,
        "validation_token": None,
        "client_context": {},
        "execution_logs": [],
        "outcomes": [],
        "mode": "normal",
        "errors": []
    }

    # 3. Execute Workflow
    print("Starting Revenue Automation Workflow...")
    final_state = await app.ainvoke(initial_state)
    
    print("\n--- WORKFLOW SUMMARY ---")
    print(f"Signals Processed: {len(final_state['signals'])}")
    print(f"Executions Performed: {len(final_state['execution_logs'])}")
    if final_state.get("is_blocked"):
        print(f"Status: BLOCKED - {final_state.get('blocking_reason')}")
    else:
        print("Status: COMPLETED")

if __name__ == "__main__":
    asyncio.run(run_sample())
