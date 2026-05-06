from typing import Dict, Any, List
import uuid
import numpy as np
from services.workflow_engine.state import AgentState
from libs.contracts.models import RevenueCommand, ExpertOutput
from libs.telemetry.logger import AgentLogger

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

async def aggregator_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("Aggregator", tenant_id, state.get("trace_id", "unknown"))
    
    expert_outputs = state.get("expert_outputs", [])
    current_signal = state.get("current_signal")
    
    if not current_signal or not expert_outputs:
        return {"is_blocked": True, "blocking_reason": "No expert outputs to aggregate"}
    
    affinities = current_signal.expert_affinities or {}
    
    # 1. Normalize weights using softmax
    expert_names = [out.expert_name for out in expert_outputs]
    raw_scores = [affinities.get(name, 0.0) for name in expert_names]
    weights = softmax(raw_scores)
    
    weight_map = dict(zip(expert_names, weights))
    logger.info(f"Normalized weights: {weight_map}")
    
    # 2. Weighted Fusion
    merged_params = {}
    all_rationales = []
    
    # For numeric params, calculate weighted average
    # For categorical, take from expert with highest weight
    best_expert = expert_names[np.argmax(weights)]
    
    numeric_params = {}
    
    for out in expert_outputs:
        weight = weight_map[out.expert_name]
        all_rationales.append(f"[{out.expert_name}]: {out.rationale}")
        
        params = out.output.get("params", {})
        for k, v in params.items():
            if isinstance(v, (int, float)):
                if k not in numeric_params:
                    numeric_params[k] = 0.0
                numeric_params[k] += v * weight
            else:
                # Categorical: only take from the "best" expert (or overwrite if current weight is higher)
                # Here we just take from the best expert identified earlier
                if out.expert_name == best_expert:
                    merged_params[k] = v

    # Add weighted numeric params
    merged_params.update(numeric_params)
    
    command = RevenueCommand(
        command_id=str(uuid.uuid4()),
        signal_id=current_signal.signal_id,
        action_intent=current_signal.signal_type,
        approved_params=merged_params,
        guardrail_token="PENDING",
        rationale=" | ".join(all_rationales)
    )
    
    logger.info(f"Aggregation complete. Primary expert influence: {best_expert}")
    
    return {
        "active_command": command,
        "is_blocked": False
    }
