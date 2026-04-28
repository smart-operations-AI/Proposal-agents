from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import AgentState
from services.fia_service.fia_node import fia_decision_node
from services.sea_service.sea_node import sea_execution_node

# --- Node Definitions ---

async def validate_input_node(state: AgentState) -> Dict[str, Any]:
    print("--- VALIDATING INPUT ---")
    payload = state.get("input_payload")
    if not payload or not payload.predictions:
        return {"is_blocked": True, "blocking_reason": "Empty payload"}
    return {"is_blocked": False}

async def signal_normalization_node(state: AgentState) -> Dict[str, Any]:
    print("--- NORMALIZING SIGNALS ---")
    # In a real scenario, this might call the PySpark job or a lighter service
    from libs.contracts.models import InternalSignal, SignalType
    import uuid
    from datetime import datetime, timedelta
    
    signals = []
    for pred in state["input_payload"].predictions:
        signal = InternalSignal(
            signal_id=str(uuid.uuid4()),
            tenant_id=state["tenant_id"],
            client_id=pred.client_id,
            signal_type=SignalType.RETAIN if pred.model_type == "churn" else SignalType.UPSELL,
            priority_score=pred.recommended_priority,
            estimated_revenue_impact=1000.0, # Placeholder
            segment="mid_market",
            urgency_level="high" if pred.score > 0.8 else "low",
            expires_at=datetime.now() + timedelta(hours=pred.validity_window_hours)
        )
        signals.append(signal)
    
    return {"signals": signals}

async def policy_guardrails_node(state: AgentState) -> Dict[str, Any]:
    print("--- APPLYING GUARDRAILS ---")
    signal = state.get("current_signal")
    command = state.get("active_command")
    if not signal or not command:
        return {"is_blocked": True}
    
    # 1. Idempotency Check
    from libs.guardrails.idempotency import IdempotencyManager
    idem = IdempotencyManager()
    if await idem.is_duplicate(signal):
        return {"is_blocked": True, "blocking_reason": "Duplicate action within window"}

    # 2. Policy Engine Validation
    from services.policy_engine.engine import PolicyEngine
    tenant_config = state.get("tenant_config", {})
    if not tenant_config:
        # Fallback to DB if not in state
        from libs.tenants.config import TenantConfigService
        tenant_config = TenantConfigService().get_config(state["tenant_id"])
        
    policy_engine = PolicyEngine(tenant_config)
    
    # Strategic Account Escalation
    if await policy_engine.is_strategic_account(signal.client_id):
        from services.escalation_service.service import EscalationService
        esc = EscalationService(state["tenant_id"], state["trace_id"])
        await esc.escalate_to_human(signal.client_id, "Strategic Account detected", {"signal": signal.model_dump()})
        return {"is_blocked": True, "blocking_reason": "Escalated: Strategic Account"}

    is_valid, reason = await policy_engine.validate_command(command, signal)
    if not is_valid:
        return {"is_blocked": True, "blocking_reason": f"Policy Violation: {reason}"}

    # 3. Validation Token Generation
    import secrets
    validation_token = secrets.token_hex(16)
    
    return {
        "is_blocked": False,
        "validation_token": validation_token
    }

async def outcome_tracking_node(state: AgentState) -> Dict[str, Any]:
    print("--- TRACKING OUTCOMES ---")
    from services.outcome_tracker.tracker import OutcomeTracker
    from libs.contracts.models import Outcome, OutcomeStatus
    
    tracker = OutcomeTracker()
    logs = state.get("execution_logs", [])
    outcomes = []
    
    for log in logs:
        # Mocking an immediate outcome for demonstration
        # In reality, this might be triggered later by a webhook
        outcome = Outcome(
            execution_id=log.execution_id,
            signal_id=log.signal_id,
            client_id=log.client_id,
            outcome_status=OutcomeStatus.REVENUE_PROTECTED if log.status == "executed" else OutcomeStatus.FAILED,
            revenue_protected=1200.0, # Mock impact
            time_to_outcome_minutes=10,
            attribution_confidence=0.9
        )
        await tracker.record_outcome(outcome, state["tenant_id"])
        outcomes.append(outcome)
        
    return {"outcomes": outcomes}

# --- Conditional Logic ---

def should_continue(state: AgentState):
    if state.get("is_blocked"):
        return "end"
    return "continue"

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("validate", validate_input_node)
workflow.add_node("normalize", signal_normalization_node)
workflow.add_node("fia", fia_decision_node)
workflow.add_node("policy", policy_guardrails_node)
workflow.add_node("sea", sea_execution_node)
workflow.add_node("outcome", outcome_tracking_node)

workflow.set_entry_point("validate")

workflow.add_edge("validate", "normalize")
workflow.add_edge("normalize", "fia")
workflow.add_edge("fia", "policy")

workflow.add_conditional_edges(
    "policy",
    should_continue,
    {
        "continue": "sea",
        "end": END
    }
)

workflow.add_edge("sea", "outcome")
workflow.add_edge("outcome", END)

app = workflow.compile()
