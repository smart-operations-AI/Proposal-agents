from typing import Dict, Any, List
from services.workflow_engine.state import AgentState
from libs.contracts.models import ExpertOutput, SignalType
from libs.telemetry.logger import AgentLogger

async def escalation_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("Escalation-Expert", tenant_id, state.get("trace_id", "unknown"))
    logger.info("Escalation Expert evaluating signal")
    
    current_signal = state.get("current_signal")
    if not current_signal:
        return {"errors": ["No signal provided to Escalation Expert"]}

    # Logic to decide if we should escalate to human
    should_escalate = current_signal.requires_human_review or current_signal.estimated_revenue_impact > 10000
    
    expert_output = ExpertOutput(
        expert_name="escalate",
        output={
            "action_intent": SignalType.ESCALATE if should_escalate else current_signal.signal_type,
            "params": {
                "human_queue": "high_priority" if current_signal.priority_score > 80 else "default",
                "reason": "High revenue impact" if current_signal.estimated_revenue_impact > 10000 else "Standard review"
            }
        },
        confidence=1.0 if should_escalate else 0.5,
        rationale="Signal meets escalation thresholds for revenue or priority." if should_escalate else "Escalation not strictly required but available."
    )
    
    current_outputs = current_signal.expert_outputs or []
    current_outputs.append(expert_output)
    current_signal.expert_outputs = current_outputs
    
    return {
        "current_signal": current_signal
    }
