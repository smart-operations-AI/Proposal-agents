from typing import Dict, Any, List
import uuid
import json
from services.workflow_engine.state import AgentState
from libs.contracts.models import InternalSignal, SignalType, RevenueCommand, ExpertOutput
from libs.memory.chroma_store import ChromaStore
from libs.telemetry.logger import AgentLogger
from services.priority_engine.engine import PriorityEngine
from libs.tenants.config import TenantConfigService
from libs.ml.local_inference import LocalInferenceEngine

async def fia_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("FIA-Expert", tenant_id, state.get("trace_id", "unknown"))
    
    try:
        # --- Communication setup (Step 5) ---
        async def handle_risk_query(message: Any):
            logger.info(f"FIA received risk query: {message}")
            return {"advice": "Proceed with caution, client has high LTV", "extra_discount_allowed": True}
        
        await state["message_bus"].subscribe("risk_query", handle_risk_query)
        
        # --- Standard execution ---
        local_llm = LocalInferenceEngine()
        current_signal = state.get("current_signal")
        if not current_signal:
            return {"errors": ["No signal provided"]}

        if current_signal.signal_type not in [SignalType.RETAIN, SignalType.UPSELL]:
            logger.info("FIA Expert rejecting: Signal type out of domain")
            return {"expert_outputs": []}

        system_prompt = """You are a Senior Financial Intelligence Agent. 
        Analyze the signal and propose a financial strategy (discounts, ROI optimization).
        Return a JSON with: action, params, confidence, rationale."""
        
        response = await local_llm.chat(system_prompt, f"Signal: {current_signal.model_dump_json()}")
        result = json.loads(response)
        
        expert_output = ExpertOutput(
            expert_name="fia_expert",
            output={
                "action_intent": result.get("action"),
                "params": result.get("params")
            },
            confidence=result.get("confidence", 0.8),
            rationale=result.get("rationale", "Financial analysis complete.")
        )
        
        return {"expert_outputs": [expert_output]}

    except Exception as e:
        logger.error(f"FIA Expert failed: {str(e)}")
        return {"errors": [f"FIA Error: {str(e)}"]}
