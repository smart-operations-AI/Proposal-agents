from datetime import datetime
from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Enums ---

class SignalType(str, Enum):
    RETAIN = "RETAIN"
    UPSELL = "UPSELL"
    PAYMENT_RISK = "PAYMENT_RISK"
    ESCALATE = "ESCALATE"
    IGNORE = "IGNORE"

class OutcomeStatus(str, Enum):
    REVENUE_GENERATED = "revenue_generated"
    REVENUE_PROTECTED = "revenue_protected"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    FAILED = "failed"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    RETRYING = "retrying"
    FAILED = "failed"

# --- Input Payloads ---

class PredictionEntry(BaseModel):
    client_id: str
    model_type: str
    score: float
    predicted_value: str
    prediction_timestamp: datetime
    validity_window_hours: int
    recommended_priority: int

class InputPayload(BaseModel):
    tenant_id: str
    batch_id: str
    model_version: str
    predictions: List[PredictionEntry]

# --- Internal Signals ---

class InternalSignal(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    
    signal_id: str
    tenant_id: str
    client_id: str
    signal_type: SignalType
    priority_score: int = Field(ge=0, le=100)
    estimated_revenue_impact: float
    segment: str
    max_discount_pct: Optional[float] = None
    urgency_level: str
    requires_human_review: bool = False
    expires_at: datetime
    rationale: str = Field(description="Agent's reasoning for this signal")
    metadata: dict = Field(default_factory=dict)

class RevenueCommand(BaseModel):
    """Explicit command from FIA to SEA"""
    command_id: str
    signal_id: str
    action_intent: SignalType
    approved_params: Dict[str, Any]
    guardrail_token: str  # Token indicating policy validation
    execution_window_hours: int = 24
    rationale: str

# --- Outcomes ---

class Outcome(BaseModel):
    execution_id: str
    signal_id: str
    client_id: str
    outcome_status: OutcomeStatus
    revenue_generated: float = 0.0
    revenue_protected: float = 0.0
    time_to_outcome_minutes: int
    attribution_confidence: float
    escalation_reason: Optional[str] = None
    rejection_reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# --- Execution ---

class ExecutionLog(BaseModel):
    execution_id: str
    signal_id: str
    client_id: str
    action_type: str
    channel: str
    scheduled_at: datetime
    executed_at: Optional[datetime] = None
    status: ExecutionStatus
    retry_count: int = 0
    payload_sent: dict = Field(default_factory=dict)
    response_received: Optional[dict] = None
