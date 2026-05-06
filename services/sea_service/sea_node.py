from typing import Dict, Any, List
from datetime import datetime
import uuid
import json
from services.workflow_engine.state import AgentState
from libs.ml.local_inference import LocalInferenceEngine
from libs.contracts.models import ExpertOutput, SignalType, ExecutionLog, ExecutionStatus
from libs.telemetry.logger import AgentLogger
from libs.adapters.context import (
    crm_adapter_ctx, 
    erp_adapter_ctx, 
    whatsapp_adapter_ctx, 
    email_adapter_ctx
)

async def sea_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("SEA-Expert", tenant_id, state.get("trace_id", "unknown"))
    
    try:
        local_llm = LocalInferenceEngine()
        current_signal = state.get("current_signal")
        if not current_signal:
            return {"errors": ["No signal provided"]}

        if current_signal.signal_type not in [SignalType.RETAIN, SignalType.UPSELL]:
            logger.info("SEA Expert rejecting: Signal type out of domain")
            return {"expert_outputs": []}

        system_prompt = """You are a Senior Sales Execution Agent.
        Propose the best outreach strategy (channels, tone, timing).
        Return a JSON with: action, params, confidence, rationale."""
        
        response = await local_llm.chat(system_prompt, f"Signal: {current_signal.model_dump_json()}")
        result = json.loads(response)
        
        expert_output = ExpertOutput(
            expert_name="sea_expert",
            output={
                "action_intent": result.get("action"),
                "params": result.get("params")
            },
            confidence=result.get("confidence", 0.8),
            rationale=result.get("rationale", "Sales strategy optimized.")
        )
        
        return {"expert_outputs": [expert_output]}

    except Exception as e:
        logger.error(f"SEA Expert failed: {str(e)}")
        return {"errors": [f"SEA Error: {str(e)}"]}

async def sea_execution_node(state: AgentState) -> Dict[str, Any]:
    command = state.get("active_command")
    token = state.get("validation_token")
    
    if not command or not token:
        return {"is_blocked": True, "blocking_reason": "Security: Missing validation token"}

    print(f"--- SEA Executing Command {command.command_id} ---")
    
    signal = state.get("current_signal")
    if not signal:
        return {}
    
    # Dependency Injection: Get adapters from context
    crm = crm_adapter_ctx.get()
    erp = erp_adapter_ctx.get()
    whatsapp = whatsapp_adapter_ctx.get()
    email = email_adapter_ctx.get()
    
    execution_id = str(uuid.uuid4())
    logs = state.get("execution_logs", [])
    
    try:
        # Execution Strategy
        if signal.signal_type == SignalType.PAYMENT_RISK:
            if erp: await erp.apply_operational_change(signal.client_id, "CREDIT_HOLD", {"reason": "Risk"})
            if crm: await crm.create_task(signal.client_id, "Urgent: Payment Risk", "Review credit")
            if whatsapp: await whatsapp.send_message(signal.client_id, "Reminder: payment overdue")
            channel = "ERP/CRM/WHATSAPP"
            
        elif signal.signal_type == SignalType.RETAIN:
            if email: await email.send_message(signal.client_id, f"Special offer: {signal.max_discount_pct}%")
            if crm: await crm.create_task(signal.client_id, "Retention Outreach", f"Follow up")
            channel = "EMAIL/CRM"
            
        else:
            channel = "NONE"

        log = ExecutionLog(
            execution_id=execution_id,
            signal_id=signal.signal_id,
            client_id=signal.client_id,
            action_type=str(signal.signal_type),
            channel=channel,
            scheduled_at=datetime.now(),
            executed_at=datetime.now(),
            status=ExecutionStatus.EXECUTED,
            payload_sent={"signal": signal.model_dump()}
        )
        logs.append(log)
        
    except Exception as e:
        log = ExecutionLog(
            execution_id=execution_id,
            signal_id=signal.signal_id,
            client_id=signal.client_id,
            action_type=str(signal.signal_type),
            channel="FAILED",
            scheduled_at=datetime.now(),
            status=ExecutionStatus.FAILED,
            response_received={"error": str(e)}
        )
        logs.append(log)
    
    return {"execution_logs": logs}
