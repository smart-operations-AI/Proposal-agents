from fastapi import FastAPI, HTTPException, BackgroundTasks
from libs.contracts.models import InputPayload
from services.workflow_engine.graph import app as workflow_app
import uuid
from datetime import datetime

api = FastAPI(title="Dataizen Model Gateway")

@api.post("/v1/predictions")
async def receive_predictions(payload: InputPayload, background_tasks: BackgroundTasks):
    """
    Endpoint to receive batches of predictions from Dataizen or ML models.
    """
    trace_id = f"trace_{uuid.uuid4().hex}"
    
    # Process in background to return 202 quickly
    background_tasks.add_task(
        run_workflow, payload, trace_id
    )
    
    return {
        "status": "accepted",
        "trace_id": trace_id,
        "received_at": datetime.now()
    }

async def run_workflow(payload: InputPayload, trace_id: str):
    initial_state = {
        "tenant_id": payload.tenant_id,
        "trace_id": trace_id,
        "input_payload": payload,
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
    await workflow_app.ainvoke(initial_state)
