import pytest
from unittest.mock import AsyncMock, patch
from services.workflow_engine.graph import get_app
from libs.contracts.models import InputPayload, PredictionEntry
from datetime import datetime

@pytest.mark.asyncio
async def test_workflow_error_routing():
    """
    Verifies that if an expert node fails, the graph correctly routes to the error_handler.
    """
    with patch("services.workflow_engine.graph.AsyncPostgresSaver"), \
         patch("services.workflow_engine.graph.create_async_engine"), \
         patch("services.fia_service.fia_node.LocalInferenceEngine.chat", side_effect=Exception("Ollama Down")):

        app = await get_app()
        
        payload = InputPayload(
            tenant_id="tenant_err",
            batch_id="b_err",
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
            "tenant_id": "tenant_err",
            "trace_id": "t_err",
            "input_payload": payload,
            "signals": [],
            "expert_outputs": [],
            "current_signal": None,
            "is_blocked": False,
            "errors": [],
            "selected_experts": ["fia_expert"]
        }
        
        # Execute
        result = await app.ainvoke(initial_state)
        
        # Assertions
        assert result["is_blocked"] is True
        assert any("FIA Error: Ollama Down" in err for err in result["errors"])
        assert "System Error:" in result["blocking_reason"]
