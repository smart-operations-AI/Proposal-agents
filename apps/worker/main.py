import asyncio
from datetime import datetime
from libs.contracts.models import InputPayload, PredictionEntry
from services.workflow_engine.graph import get_app
from libs.persistence.database import init_db, get_engine
from libs.adapters.context import crm_adapter_ctx, erp_adapter_ctx, whatsapp_adapter_ctx, email_adapter_ctx
from unittest.mock import MagicMock

async def run_sample():
    # 0. Initialize DB and Seed Config
    # In a real environment, you'd have actual DB and Redis running
    # For the demo, we ensure the structure is correct
    
    # engine = get_engine()
    # init_db(engine)
    
    # --- Step 7: Inject Adapters (DI) ---
    crm_adapter_ctx.set(MagicMock(name="SalesforceCRM"))
    erp_adapter_ctx.set(MagicMock(name="SAPERP"))
    whatsapp_adapter_ctx.set(MagicMock(name="WhatsApp"))
    email_adapter_ctx.set(MagicMock(name="Email"))
    
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
            )
        ]
    )

    # 2. Initialize State
    initial_state = {
        "tenant_id": "tenant_001",
        "trace_id": f"trace_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "input_payload": sample_payload,
        "signals": [],
        "expert_outputs": [],
        "message_bus": None, # Initialized in validate_input_node
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

    # 3. Compile and Execute Workflow
    print("Starting Revenue MoE Workflow...")
    app = await get_app()
    
    try:
        final_state = await app.ainvoke(initial_state)
        
        print("\n--- WORKFLOW SUMMARY ---")
        print(f"Signals Normalized: {len(final_state.get('signals', []))}")
        print(f"Experts Responded: {len(final_state.get('expert_outputs', []))}")
        print(f"Executions Performed: {len(final_state.get('execution_logs', []))}")
        
        if final_state.get("is_blocked"):
            print(f"Status: BLOCKED - {final_state.get('blocking_reason')}")
        else:
            print("Status: COMPLETED")
            if final_state.get("active_command"):
                print(f"Command Rationale: {final_state['active_command'].rationale}")
    except Exception as e:
        print(f"Workflow failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_sample())
