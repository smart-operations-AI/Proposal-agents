from typing import Dict, Any
import uuid
from services.workflow_engine.state import AgentState
from libs.contracts.models import InternalSignal, SignalType, RevenueCommand, ExpertOutput
from libs.memory.chroma_store import ChromaStore
from libs.telemetry.logger import AgentLogger
from services.priority_engine.engine import PriorityEngine
from libs.tenants.config import TenantConfigService

async def fia_decision_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("FIA", tenant_id, state.get("trace_id", "unknown"))
    logger.info("Starting FIA Decision Process")
    
    # 1. Load Tenant Config (No more defaults)
    config_service = TenantConfigService()
    tenant_config = config_service.get_config(tenant_id)
    if not tenant_config:
        return {"is_blocked": True, "blocking_reason": f"No configuration found for tenant {tenant_id}"}
    
    signals = state.get("signals", [])
    if not signals:
        return {"is_blocked": True, "blocking_reason": "No signals to process"}

    # 2. Ranking through Priority Engine
    priority_engine = PriorityEngine()
    ranked_signals = priority_engine.rank_signals(signals)
    current_signal = ranked_signals[0]
    
    # 3. Retrieval of Context (RAG)
    memory = ChromaStore()
    context = memory.query_policies(
        tenant_id=tenant_id,
        query_text=f"Playbook for {current_signal.signal_type}"
    )
    
    # 4. Decision Rationale using Config data
    exec_cost = tenant_config.get("standard_execution_cost", 0.0)
    roi = priority_engine.calculate_roi(current_signal, exec_cost)
    rationale = f"Selected {current_signal.signal_type} for {current_signal.client_id}. ROI: {roi:.2f} (Cost: {exec_cost})."
    
    # 5. Create Command using Config parameters
    command = RevenueCommand(
        command_id=str(uuid.uuid4()),
        signal_id=current_signal.signal_id,
        action_intent=current_signal.signal_type,
        approved_params={
            "max_discount": current_signal.max_discount_pct or tenant_config.get("default_offer_discount", 0.0),
            "roi": roi,
            "channel_preference": tenant_config.get("preferred_channel", "EMAIL")
        },
        guardrail_token="PENDING",
        rationale=rationale
    )
    
    return {
        "current_signal": current_signal,
        "active_command": command,
        "is_blocked": False,
        "tenant_config": tenant_config # Pass it down to avoid multiple DB hits
    }

from libs.ml.local_inference import LocalInferenceEngine
import json

async def fia_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("FIA-Expert", tenant_id, state.get("trace_id", "unknown"))
    local_llm = LocalInferenceEngine()
    
    current_signal = state.get("current_signal")
    if not current_signal:
        return {"errors": ["No signal provided"]}

    # 1. Rejection Logic: Is this signal within financial domain?
    if current_signal.signal_type not in [SignalType.RETAIN, SignalType.UPSELL]:
        logger.info("FIA Expert rejecting: Signal type out of domain")
        return {"expert_outputs": current_signal.expert_outputs}

    # 2. Local Inference with System Prompt
    system_prompt = """You are a Senior Financial Intelligence Agent. 
    Analyze the signal and propose a financial strategy (discounts, ROI optimization).
    Return a JSON with: action, params, confidence, rationale."""
    
    response = await local_llm.chat(system_prompt, f"Signal: {current_signal.model_dump_json()}")
    result = json.loads(response)
    
    # 3. Create Expert Output
    expert_output = ExpertOutput(
        expert_name="fia_expert",
        output={
            "action_intent": result.get("action"),
            "params": result.get("params")
        },
        confidence=result.get("confidence", 0.8),
        rationale=result.get("rationale", "Financial analysis complete.")
    )
    
    current_outputs = current_signal.expert_outputs or []
    current_outputs.append(expert_output)
    current_signal.expert_outputs = current_outputs
    
    return {"current_signal": current_signal}
