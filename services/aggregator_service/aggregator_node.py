from typing import Dict, Any, List
import uuid
from services.workflow_engine.state import AgentState
from libs.contracts.models import RevenueCommand, ExpertOutput
from libs.telemetry.logger import AgentLogger

async def aggregator_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("Aggregator", tenant_id, state.get("trace_id", "unknown"))
    logger.info("Starting Weighted Aggregation")
    
    current_signal = state.get("current_signal")
    if not current_signal or not current_signal.expert_outputs:
        return {"is_blocked": True, "blocking_reason": "No expert outputs to aggregate"}
    
    expert_outputs = current_signal.expert_outputs
    affinities = current_signal.expert_affinities
    
    # Conflict Resolution: Weighted scoring
    # final_params = sum(weight * value) / sum(weight) -- for numeric
    # For categorical, we take the one with the highest weight * confidence
    
    weighted_scores = []
    for out in expert_outputs:
        weight = affinities.get(out.expert_name, 0.0)
        score = weight * out.confidence
        weighted_scores.append((out, score))
        
    # Sort by weighted score
    weighted_scores.sort(key=lambda x: x[1], reverse=True)
    best_expert_out, top_score = weighted_scores[0]
    
    # Merge Logic
    merged_params = {}
    all_rationales = []
    
    # Simple merge: collect all unique params, overwrite with higher score
    for out, score in reversed(weighted_scores): # Process low score first so high score overwrites
        merged_params.update(out.output.get("params", {}))
        all_rationales.append(f"[{out.expert_name}]: {out.rationale}")
        
    command = RevenueCommand(
        command_id=str(uuid.uuid4()),
        signal_id=current_signal.signal_id,
        action_intent=best_expert_out.output.get("action_intent", current_signal.signal_type),
        approved_params=merged_params,
        guardrail_token="PENDING",
        rationale=" | ".join(all_rationales)
    )
    
    logger.info(f"Aggregation complete. Primary expert: {best_expert_out.expert_name}")
    
    return {
        "active_command": command,
        "is_blocked": False
    }
