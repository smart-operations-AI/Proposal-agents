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

async def fia_expert_node(state: AgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    logger = AgentLogger("FIA-Expert", tenant_id, state.get("trace_id", "unknown"))
    logger.info("FIA Expert processing signal")
    
    current_signal = state.get("current_signal")
    if not current_signal:
        return {"errors": ["No signal provided to FIA Expert"]}

    # 1. Load Tenant Config
    config_service = TenantConfigService()
    tenant_config = config_service.get_config(tenant_id)
    
    # 2. Retrieval of Context (Private Memory)
    memory = ChromaStore()
    context = memory.query_policies(
        tenant_id=tenant_id,
        query_text=f"Financial strategy for {current_signal.signal_type}",
        namespace="fia_expert" # Private memory namespace
    )
    
    # 3. Decision Logic
    priority_engine = PriorityEngine()
    exec_cost = (tenant_config or {}).get("standard_execution_cost", 50.0)
    roi = priority_engine.calculate_roi(current_signal, exec_cost)
    
    # Check if we should decline
    if roi < 1.0 and current_signal.urgency_level != "high":
        logger.info("FIA Expert declining: Low ROI")
        return {"expert_outputs": []} # Decline processing

    expert_output = ExpertOutput(
        expert_name="fia_expert",
        output={
            "action_intent": current_signal.signal_type,
            "params": {
                "max_discount": current_signal.max_discount_pct or (tenant_config or {}).get("default_offer_discount", 0.1),
                "roi": roi
            }
        },
        confidence=0.9 if roi > 2.0 else 0.7,
        rationale=f"High ROI detected ({roi:.2f}). Financial context applied."
    )
    
    # Append to existing outputs
    current_outputs = current_signal.expert_outputs or []
    current_outputs.append(expert_output)
    current_signal.expert_outputs = current_outputs
    
    return {
        "current_signal": current_signal
    }
