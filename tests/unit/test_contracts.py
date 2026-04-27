import pytest
from datetime import datetime
from libs.contracts.models import InputPayload, PredictionEntry

def test_input_payload_validation():
    data = {
        "tenant_id": "t1",
        "batch_id": "b1",
        "model_version": "v1",
        "predictions": [
            {
                "client_id": "c1",
                "model_type": "churn",
                "score": 0.5,
                "predicted_value": "mid",
                "prediction_timestamp": datetime.now().isoformat(),
                "validity_window_hours": 24,
                "recommended_priority": 50
            }
        ]
    }
    payload = InputPayload(**data)
    assert payload.tenant_id == "t1"
    assert len(payload.predictions) == 1
    assert payload.predictions[0].client_id == "c1"

def test_invalid_input_payload():
    with pytest.raises(Exception):
        InputPayload(tenant_id="t1") # Missing required fields
