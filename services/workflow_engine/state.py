from typing import TypedDict, List, Optional, Dict, Any, Annotated
from libs.contracts.models import InternalSignal, Outcome, ExecutionLog, InputPayload, RevenueCommand, ExpertOutput
from libs.communication.message_bus import AgentMessageBus
import operator

class AgentState(TypedDict):
    # Workflow Context
    tenant_id: str
    trace_id: str
    input_payload: InputPayload
    
    # Processed Data
    signals: List[InternalSignal]
    
    # MoE Multi-Agent Fields
    selected_experts: List[str]
    routing_rationale: Optional[str]
    
    # NEW: Aggregated Expert Outputs with Reducer for Parallelism
    expert_outputs: Annotated[List[ExpertOutput], operator.add]
    
    # Message Bus for lateral communication
    message_bus: AgentMessageBus
    
    # Intelligence Layer Output
    current_signal: Optional[InternalSignal]
    active_command: Optional[RevenueCommand]
    
    # Guardrail Results
    is_blocked: bool
    blocking_reason: Optional[str]
    validation_token: Optional[str]
    
    # Infrastructure Layer Data (Enriched)
    client_context: Dict[str, Any]
    
    # Execution
    execution_logs: List[ExecutionLog]
    outcomes: List[Outcome]
    
    # Control Flags
    mode: str  # "normal", "freeze", "dry_run"
    
    # Errors
    errors: List[str]
