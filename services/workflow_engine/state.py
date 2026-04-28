from typing import TypedDict, List, Optional, Dict, Any
from libs.contracts.models import InternalSignal, Outcome, ExecutionLog, InputPayload, RevenueCommand

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
