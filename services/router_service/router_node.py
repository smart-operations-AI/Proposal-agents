from typing import Dict, Any, List
from services.workflow_engine.state import AgentState
from libs.contracts.models import SignalType
from libs.telemetry.logger import AgentLogger
from libs.telemetry.metrics import MetricsManager

async def router_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("Router", tenant_id, state.get("trace_id", "unknown"))
    metrics = MetricsManager()
    
    signals = state.get("signals", [])
    if not signals:
        return {"is_blocked": True, "blocking_reason": "No signals to route"}
    
    current_signal = signals[0]
    
    # 1. Base Affinities (In Phase 4, this would be LLM/Embedding based)
    base_affinities = {
        "fia_expert": 0.8 if current_signal.signal_type in [SignalType.RETAIN, SignalType.UPSELL] else 0.2,
        "sea_expert": 0.7 if current_signal.signal_type in [SignalType.RETAIN, SignalType.UPSELL] else 0.3,
        "risk_expert": 0.9 if current_signal.signal_type == SignalType.PAYMENT_RISK else 0.1,
        "escalate": 0.9 if current_signal.requires_human_review else 0.05
    }
    
    # 2. Auxiliary Loss: Load Balance Penalty
    # We penalize experts that have been used too much
    utilization = metrics.get_utilization_rates()
    adjusted_affinities = {}
    for expert, affinity in base_affinities.items():
        penalty = utilization.get(expert, 0) * 0.2 # 20% penalty for high utilization
        adjusted_affinities[expert] = max(0, affinity - penalty)
    
    # 3. Top-k Gating (k=2)
    k = 2
    sorted_experts = sorted(adjusted_affinities.items(), key=lambda x: x[1], reverse=True)
    selected_experts = [exp for exp, score in sorted_experts[:k] if score > 0.3]
    
    if not selected_experts:
        selected_experts = [sorted_experts[0][0]] # Fallback to best one
        
    rationale = f"Selected experts {selected_experts} based on signal type {current_signal.signal_type} and load balancing."
    
    # Update metrics
    metrics.log_routing(selected_experts)
    
    # Update signal
    current_signal.expert_affinities = adjusted_affinities
    current_signal.routing_rationale = rationale
    
    logger.info("Routing complete", extra={"selected": selected_experts, "utilization": utilization})
    
    return {
        "current_signal": current_signal,
        "selected_experts": selected_experts,
        "routing_rationale": rationale,
        "is_blocked": False
    }
