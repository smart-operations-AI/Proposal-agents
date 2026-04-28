from typing import Dict, Any
from services.workflow_engine.state import AgentState
from libs.telemetry.logger import AgentLogger
from libs.telemetry.metrics import MetricsManager
from libs.ml.local_inference import LocalInferenceEngine
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

async def router_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("Router", tenant_id, state.get("trace_id", "unknown"))
    metrics = MetricsManager()
    local_llm = LocalInferenceEngine()
    
    signals = state.get("signals", [])
    if not signals:
        return {"is_blocked": True, "blocking_reason": "No signals"}
    
    current_signal = signals[0]
    
    # Expert Definitions (Semantic Profiles)
    expert_profiles = {
        "fia_expert": "financial intelligence revenue optimization ROI discount pricing",
        "sea_expert": "sales execution outreach channels messaging WhatsApp email conversion",
        "risk_expert": "risk assessment credit default payment security policy",
        "escalate": "human review urgent complex high value strategic account"
    }
    
    # 1. Semantic Affinity Calculation
    signal_text = f"{current_signal.signal_type} {current_signal.segment} {current_signal.urgency_level}"
    signal_emb = await local_llm.get_embeddings(signal_text)
    
    affinities = {}
    for expert, profile in expert_profiles.items():
        profile_emb = await local_llm.get_embeddings(profile)
        affinities[expert] = cosine_similarity(signal_emb, profile_emb)
        
    # 2. Auxiliary Loss: Load Balance Penalty
    utilization = metrics.get_utilization_rates()
    adjusted_affinities = {}
    for expert, affinity in affinities.items():
        # Subtract penalty based on utilization (Auxiliary Loss simulation)
        penalty = utilization.get(expert, 0) * 0.3 
        adjusted_affinities[expert] = max(0, affinity - penalty)
        
    # 3. Top-k Gating (k=2)
    k = 2
    sorted_experts = sorted(adjusted_affinities.items(), key=lambda x: x[1], reverse=True)
    selected_experts = [exp for exp, score in sorted_experts[:k] if score > 0.4]
    
    if not selected_experts:
        selected_experts = [sorted_experts[0][0]]
        
    rationale = f"Semantic affinity scores: { {k: round(v, 2) for k, v in affinities.items()} }. " \
                f"Selected {selected_experts} after load penalty."
    
    # Update metrics and signal
    metrics.log_routing(selected_experts)
    current_signal.expert_affinities = adjusted_affinities
    current_signal.routing_rationale = rationale
    
    logger.info("Routing decision complete", extra={"selected": selected_experts})
    
    return {
        "current_signal": current_signal,
        "selected_experts": selected_experts,
        "is_blocked": False
    }
