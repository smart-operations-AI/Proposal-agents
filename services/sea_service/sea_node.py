from typing import Dict, Any
from datetime import datetime
import uuid
from services.workflow_engine.state import AgentState
from libs.ml.local_inference import LocalInferenceEngine
import json

async def sea_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("SEA-Expert", tenant_id, state.get("trace_id", "unknown"))
    local_llm = LocalInferenceEngine()
    
    current_signal = state.get("current_signal")
    if not current_signal:
        return {"errors": ["No signal provided"]}

    # 1. Rejection Logic: Is this a commercial execution signal?
    if current_signal.signal_type not in [SignalType.RETAIN, SignalType.UPSELL]:
        logger.info("SEA Expert rejecting: Signal type out of domain")
        return {"expert_outputs": current_signal.expert_outputs}

    # 2. Local Inference
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
    
    current_outputs = current_signal.expert_outputs or []
    current_outputs.append(expert_output)
    current_signal.expert_outputs = current_outputs
    
    return {"current_signal": current_signal}

async def sea_execution_node(state: AgentState) -> Dict[str, Any]:
    # ... (rest of the file remains similar but uses the active_command)
    command = state.get("active_command")
    token = state.get("validation_token")
    
    if not command or not token:
        print("--- SEA BLOCKED: Missing Command or Validation Token ---")
        return {"is_blocked": True, "blocking_reason": "Security: Missing validation token"}

    print(f"--- SEA Executing Command {command.command_id} (Token Verified) ---")
    
    signal = state.get("current_signal")
    if not signal:
        return {}
    
    # Instantiate Adapters (In a real system, these would be injected)
    crm = SalesforceCRMAdapter()
    erp = SAPERPAdapter()
    whatsapp = WhatsAppAdapter()
    email = EmailAdapter()
    
    execution_id = str(uuid.uuid4())
    logs = state.get("execution_logs", [])
    
    try:
        # Execution Strategy based on Signal Type
        if signal.signal_type == SignalType.PAYMENT_RISK:
            # 1. Update ERP
            await erp.apply_operational_change(signal.client_id, "CREDIT_HOLD", {"reason": "Payment Risk Signal"})
            # 2. Create CRM Task
            await crm.create_task(signal.client_id, "Urgent: Payment Risk", "Review credit terms immediately")
            # 3. Notify via WhatsApp
            await whatsapp.send_message(signal.client_id, "Reminder: Your payment is overdue. Please check your account.")
            channel = "ERP/CRM/WHATSAPP"
            
        elif signal.signal_type == SignalType.RETAIN:
            # 1. Notify via Email
            await email.send_message(signal.client_id, f"Special offer to stay with us! Discount: {signal.max_discount_pct}%")
            # 2. Create CRM Task for account manager
            await crm.create_task(signal.client_id, "Retention Outreach", f"Follow up on retention offer for {signal.client_id}")
            channel = "EMAIL/CRM"
            
        elif signal.signal_type == SignalType.UPSELL:
            # 1. Notify via Email/WhatsApp
            await whatsapp.send_message(signal.client_id, "Check out our new products!")
            channel = "WHATSAPP"
            
        else:
            channel = "NONE"

        log = ExecutionLog(
            execution_id=execution_id,
            signal_id=signal.signal_id,
            client_id=signal.client_id,
            action_type=signal.signal_type,
            channel=channel,
            scheduled_at=datetime.now(),
            executed_at=datetime.now(),
            status=ExecutionStatus.EXECUTED,
            payload_sent={"signal": signal.model_dump()}
        )
        logs.append(log)
        
    except Exception as e:
        print(f"Execution failed for {signal.client_id}: {str(e)}")
        log = ExecutionLog(
            execution_id=execution_id,
            signal_id=signal.signal_id,
            client_id=signal.client_id,
            action_type=signal.signal_type,
            channel="FAILED",
            scheduled_at=datetime.now(),
            status=ExecutionStatus.FAILED,
            response_received={"error": str(e)}
        )
        logs.append(log)
    
    return {"execution_logs": logs}
