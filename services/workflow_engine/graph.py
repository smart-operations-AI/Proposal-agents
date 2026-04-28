from .state import AgentState
from services.router_service.router_node import router_node
from services.fia_service.fia_node import fia_expert_node
from services.sea_service.sea_node import sea_expert_node
from services.risk_service.risk_node import risk_expert_node
from services.escalation_service.escalation_expert_node import escalation_expert_node
from services.aggregator_service.aggregator_node import aggregator_node
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
            estimated_revenue_impact=1000.0,
            segment="mid_market",
            urgency_level="high" if pred.score > 0.8 else "low",
            expires_at=datetime.now() + timedelta(hours=pred.validity_window_hours),
            rationale="Initial normalization"
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
    tenant_config = state.get("tenant_config", {}) or {}
    policy_engine = PolicyEngine(tenant_config)
    
    is_valid, reason = await policy_engine.validate_command(command, signal)
    if not is_valid:
        return {"is_blocked": True, "blocking_reason": f"Policy Violation: {reason}"}

    # 3. Validation Token Generation
    import secrets
    return {"is_blocked": False, "validation_token": secrets.token_hex(16)}

async def outcome_tracking_node(state: AgentState) -> Dict[str, Any]:
    print("--- TRACKING OUTCOMES ---")
    from services.outcome_tracker.tracker import OutcomeTracker
    from libs.contracts.models import Outcome, OutcomeStatus
    
    tracker = OutcomeTracker()
    logs = state.get("execution_logs", [])
    outcomes = []
    for log in logs:
        outcome = Outcome(
            execution_id=log.execution_id,
            signal_id=log.signal_id,
            client_id=log.client_id,
            outcome_status=OutcomeStatus.REVENUE_PROTECTED if log.status == "executed" else OutcomeStatus.FAILED,
            revenue_protected=1000.0,
            time_to_outcome_minutes=10,
            attribution_confidence=0.9
        )
        await tracker.record_outcome(outcome, state["tenant_id"])
        outcomes.append(outcome)
    return {"outcomes": outcomes}

# --- Routing Logic ---

def route_to_experts(state: AgentState):
    # This function returns the list of nodes to visit
    # In Phase 2/3, we might visit only one, but MoE allows k > 1
    return state.get("selected_experts", ["fia_expert"])

def should_continue(state: AgentState):
    if state.get("is_blocked"):
        return "end"
    return "continue"

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("validate", validate_input_node)
workflow.add_node("normalize", signal_normalization_node)
workflow.add_node("router", router_node)
workflow.add_node("fia_expert", fia_expert_node)
workflow.add_node("sea_expert", sea_expert_node)
workflow.add_node("risk_expert", risk_expert_node)
workflow.add_node("escalate", escalation_expert_node)
workflow.add_node("aggregator", aggregator_node)
workflow.add_node("policy", policy_guardrails_node)
workflow.add_node("sea_execution", sea_execution_node)
workflow.add_node("outcome", outcome_tracking_node)

workflow.set_entry_point("validate")

workflow.add_edge("validate", "normalize")
workflow.add_edge("normalize", "router")

# Conditional routing to experts
workflow.add_conditional_edges(
    "router",
    route_to_experts,
    {
        "fia_expert": "fia_expert",
        "sea_expert": "sea_expert",
        "risk_expert": "risk_expert",
        "escalate": "escalate"
    }
)

# All experts lead to aggregator
workflow.add_edge("fia_expert", "aggregator")
workflow.add_edge("sea_expert", "aggregator")
workflow.add_edge("risk_expert", "aggregator")
workflow.add_edge("escalate", "aggregator")

workflow.add_edge("aggregator", "policy")

workflow.add_conditional_edges(
    "policy",
    should_continue,
    {
        "continue": "sea_execution",
        "end": END
    }
)

workflow.add_edge("sea_execution", "outcome")
workflow.add_edge("outcome", END)

app = workflow.compile()
