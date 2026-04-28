from typing import Dict, Any, List
from services.workflow_engine.state import AgentState
from libs.contracts.models import ExpertOutput
from libs.memory.chroma_store import ChromaStore
from libs.telemetry.logger import AgentLogger

async def risk_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("Risk-Expert", tenant_id, state.get("trace_id", "unknown"))
    logger.info("Risk Expert assessing signal")
    
    current_signal = state.get("current_signal")
    if not current_signal:
        return {"errors": ["No signal provided to Risk Expert"]}

    # 1. Retrieval of Risk History
    memory = ChromaStore()
    context = memory.query_policies(
        tenant_id=tenant_id,
        query_text=f"Risk profile for client {current_signal.client_id}",
        namespace="risk_expert"
    )
    
    # 2. Risk Assessment Logic
    risk_score = 0.5 # Placeholder
    if current_signal.priority_score > 90:
        risk_score = 0.8
        
    expert_output = ExpertOutput(
        expert_name="risk_expert",
        output={
            "risk_assessment": "high" if risk_score > 0.7 else "medium",
            "score": risk_score,
            "params": {
                "require_collateral": risk_score > 0.7,
                "max_credit_extension": 0.0 if risk_score > 0.8 else 5000.0
            }
        },
        confidence=0.85,
        rationale=f"Risk score {risk_score} calculated based on priority and historical context."
    )
    
    current_outputs = current_signal.expert_outputs or []
    current_outputs.append(expert_output)
    current_signal.expert_outputs = current_outputs
    
    return {
        "current_signal": current_signal
    }
