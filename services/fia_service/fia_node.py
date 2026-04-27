from typing import Dict, Any
import uuid
from services.workflow_engine.state import AgentState
from libs.contracts.models import InternalSignal, SignalType, RevenueCommand
from libs.memory.chroma_store import ChromaStore
from libs.telemetry.logger import AgentLogger
from services.priority_engine.engine import PriorityEngine

async def fia_decision_node(state: AgentState) -> Dict[str, Any]:
    logger = AgentLogger("FIA", state["tenant_id"], state.get("trace_id", "unknown"))
    logger.info("Starting FIA Decision Process")
    
    signals = state.get("signals", [])
    if not signals:
        return {"is_blocked": True, "blocking_reason": "No signals to process"}

    # 1. Ranking through Priority Engine
    priority_engine = PriorityEngine()
    ranked_signals = priority_engine.rank_signals(signals)
    current_signal = ranked_signals[0]
    
    # 2. Retrieval of Context (RAG)
    memory = ChromaStore()
    context = memory.query_policies(
        tenant_id=state["tenant_id"],
        query_text=f"Playbook for {current_signal.signal_type}"
    )
    
    # 3. Decision Rationale
    roi = priority_engine.calculate_roi(current_signal)
    rationale = f"Selected {current_signal.signal_type} for {current_signal.client_id}. Expected ROI: {roi:.2f}. "
    
    # 4. Create Command
    command = RevenueCommand(
        command_id=str(uuid.uuid4()),
        signal_id=current_signal.signal_id,
        action_intent=current_signal.signal_type,
        approved_params={
            "max_discount": current_signal.max_discount_pct or 5.0,
            "roi": roi
        },
        guardrail_token="PENDING",
        rationale=rationale
    )
    
    return {
        "current_signal": current_signal,
        "active_command": command,
        "is_blocked": False
    }
