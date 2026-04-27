from typing import Dict, Any
import uuid
from services.workflow_engine.state import AgentState
from libs.contracts.models import InternalSignal, SignalType, RevenueCommand
from libs.memory.chroma_store import ChromaStore
from libs.telemetry.logger import AgentLogger

async def fia_decision_node(state: AgentState) -> Dict[str, Any]:
    logger = AgentLogger("FIA", state["tenant_id"], state.get("trace_id", "unknown"))
    logger.info("Starting FIA Decision Process")
    
    signals = state.get("signals", [])
    if not signals:
        return {"is_blocked": True, "blocking_reason": "No signals to process"}

    # 1. Retrieval of Context (RAG)
    memory = ChromaStore()
    current_signal = signals[0] # Top priority
    
    context = memory.query_policies(
        tenant_id=state["tenant_id"],
        query_text=f"Playbook for {current_signal.signal_type} in segment {current_signal.segment}"
    )
    
    # 2. Reasoning (Simplified)
    rationale = f"Detected {current_signal.signal_type}. Economic impact ${current_signal.estimated_revenue_impact}. "
    if context and context['documents']:
        rationale += f"Applied playbook rules: {context['documents'][0][:50]}..."
    
    # 3. Create Explicit Command
    command = RevenueCommand(
        command_id=str(uuid.uuid4()),
        signal_id=current_signal.signal_id,
        action_intent=current_signal.signal_type,
        approved_params={
            "max_discount": current_signal.max_discount_pct or 5.0,
            "channel_preference": "WHATSAPP" if current_signal.urgency_level == "high" else "EMAIL"
        },
        guardrail_token="PENDING", # To be filled by Policy Engine
        rationale=rationale
    )
    
    logger.info("FIA Decision Made", command_id=command.command_id, intent=command.action_intent)
    
    return {
        "current_signal": current_signal,
        "active_command": command,
        "is_blocked": False
    }
