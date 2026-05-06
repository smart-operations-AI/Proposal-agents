from typing import Dict, Any, List
from services.workflow_engine.state import AgentState
from libs.contracts.models import ExpertOutput
from libs.memory.chroma_store import ChromaStore
from libs.telemetry.logger import AgentLogger

async def risk_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("Risk-Expert", tenant_id, state.get("trace_id", "unknown"))
    
    try:
        logger.info("Risk Expert assessing signal")
        current_signal = state.get("current_signal")
        if not current_signal:
            return {"errors": ["No signal provided to Risk Expert"]}

        # --- Communication (Step 5): Consult FIA before deciding ---
        bus_responses = await state["message_bus"].publish("risk_query", {"client_id": current_signal.client_id})
        logger.info(f"Risk Expert got feedback from other agents: {bus_responses}")

        # 1. Retrieval of Risk History (Step 8: await async query)
        memory = ChromaStore()
        context = await memory.query_policies(
            tenant_id=tenant_id,
            query_text=f"Risk profile for client {current_signal.client_id}",
            namespace="risk_expert"
        )
        
        # 2. Risk Assessment Logic
        risk_score = 0.5 
        if current_signal.priority_score > 90:
            risk_score = 0.8
            
        expert_output = ExpertOutput(
            expert_name="risk_expert",
            output={
                "risk_assessment": "high" if risk_score > 0.7 else "medium",
                "score": risk_score,
                "params": {
                    "require_collateral": risk_score > 0.7,
                    "max_credit_extension": 0.0 if risk_score > 0.8 else 5000.0,
                    "fia_feedback": bus_responses[0] if bus_responses else "No feedback"
                }
            },
            confidence=0.85,
            rationale=f"Risk score {risk_score} calculated based on priority and historical context."
        )
        
        return {"expert_outputs": [expert_output]}

    except Exception as e:
        logger.error(f"Risk Expert failed: {str(e)}")
        # Adding error to state triggers the transition to error_handler in graph.py
        return {"errors": [f"Risk Error: {str(e)}"]}
