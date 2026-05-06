import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from services.workflow_engine.graph import route_to_experts, validate_input_node
from services.aggregator_service.aggregator_node import aggregator_node
from libs.contracts.models import ExpertOutput, InternalSignal, SignalType, InputPayload, PredictionEntry
from datetime import datetime
from langgraph.types import Send

@pytest.mark.asyncio
async def test_route_to_experts_generates_send_objects():
    state = {
        "selected_experts": ["fia_expert", "sea_expert"]
    }
    result = route_to_experts(state)
    assert len(result) == 2
    assert all(isinstance(r, Send) for r in result)
    assert result[0].node == "fia_expert"
    assert result[1].node == "sea_expert"

@pytest.mark.asyncio
async def test_aggregator_merges_multiple_outputs():
    # Mock state with multiple expert outputs
    state = {
        "tenant_id": "test_tenant",
        "current_signal": MagicMock(
            signal_id="sig_123",
            signal_type=SignalType.RETAIN,
            expert_affinities={"fia_expert": 0.8, "sea_expert": 0.2}
        ),
        "expert_outputs": [
            ExpertOutput(
                expert_name="fia_expert",
                output={"params": {"discount": 10.0, "reason": "high_ltv"}},
                confidence=0.9,
                rationale="FIA rationale"
            ),
            ExpertOutput(
                expert_name="sea_expert",
                output={"params": {"discount": 15.0, "channel": "whatsapp"}},
                confidence=0.7,
                rationale="SEA rationale"
            )
        ]
    }
    
    with patch("services.aggregator_service.aggregator_node.softmax", return_value=[0.8, 0.2]):
        result = await aggregator_node(state)
        
        command = result["active_command"]
        # Discount should be weighted average: 10*0.8 + 15*0.2 = 8 + 3 = 11.0
        assert command.approved_params["discount"] == 11.0
        assert command.approved_params["reason"] == "high_ltv"
        assert "FIA rationale" in command.rationale
        assert "SEA rationale" in command.rationale

@pytest.mark.asyncio
async def test_message_bus_communication():
    from libs.communication.message_bus import AgentMessageBus
    bus = AgentMessageBus()
    
    # Mock subscriber
    handler = AsyncMock(return_value="fia_feedback")
    await bus.subscribe("risk_query", handler)
    
    # Publish
    results = await bus.publish("risk_query", {"test": "data"})
    assert results == ["fia_feedback"]
    handler.assert_called_once_with({"test": "data"})

@pytest.mark.asyncio
async def test_metrics_manager_with_mock_redis():
    with patch("redis.asyncio.Redis") as mock_redis:
        from libs.telemetry.metrics import MetricsManager
        mock_instance = mock_redis.return_value
        mock_instance.get.return_value = "10"
        mock_instance.hgetall.return_value = {"fia_expert": "5", "sea_expert": "5"}
        
        metrics = MetricsManager()
        rates = await metrics.get_utilization_rates()
        
        assert rates["fia_expert"] == 0.5
        assert rates["sea_expert"] == 0.5
