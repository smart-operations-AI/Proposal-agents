import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.workflow_engine.graph import get_app
from libs.contracts.models import InputPayload, PredictionEntry, SignalType
from datetime import datetime

@pytest.mark.asyncio
async def test_full_moe_workflow_success():
    """
    Validates the end-to-end flow of the MoE graph under normal conditions.
    """
    # Mocking external infrastructure
    with patch("services.workflow_engine.graph.AsyncPostgresSaver") as mock_saver, \
         patch("services.workflow_engine.graph.create_async_engine") as mock_engine, \
         patch("libs.ml.local_inference.LocalInferenceEngine.chat", new_callable=AsyncMock) as mock_chat, \
         patch("libs.ml.local_inference.LocalInferenceEngine.get_embeddings", new_callable=AsyncMock) as mock_emb, \
         patch("libs.telemetry.metrics.MetricsManager.get_utilization_rates", new_callable=AsyncMock) as mock_metrics, \
         patch("libs.telemetry.metrics.MetricsManager.log_routing", new_callable=AsyncMock), \
         patch("libs.telemetry.metrics.MetricsManager.close", new_callable=AsyncMock), \
         patch("libs.guardrails.idempotency.IdempotencyManager.is_duplicate", new_callable=AsyncMock) as mock_idem:

        # Setup mocks
        mock_chat.return_value = '{"action": "PROPOSE_DISCOUNT", "params": {"discount": 0.1}, "confidence": 0.9, "rationale": "Test"}'
        mock_emb.return_value = [0.1] * 384
        mock_metrics.return_value = {"fia_expert": 0.2, "sea_expert": 0.1}
        mock_idem.return_value = False
        
        # Initialize graph
        app = await get_app()
        
        # Input data
        payload = InputPayload(
            tenant_id="tenant_001",
            batch_id="b1",
            model_version="v1",
            predictions=[
                PredictionEntry(
                    client_id="c1",
                    model_type="churn",
                    score=0.9,
                    predicted_value="high",
                    prediction_timestamp=datetime.now(),
                    validity_window_hours=24,
                    recommended_priority=1
                )
            ]
        )
        
        initial_state = {
            "tenant_id": "tenant_001",
            "trace_id": "t1",
            "input_payload": payload,
            "signals": [],
            "expert_outputs": [],
            "current_signal": None,
            "is_blocked": False,
            "errors": []
        }
        
        # Execute
        result = await app.ainvoke(initial_state)
        
        # Assertions
        assert result["is_blocked"] is False
        assert len(result["signals"]) > 0
        assert result["active_command"] is not None
        assert result["active_command"].action_intent == SignalType.RETAIN
        assert "fia_expert" in [out.expert_name for out in result["expert_outputs"]]
