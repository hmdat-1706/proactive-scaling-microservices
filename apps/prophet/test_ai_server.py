import pytest
from fastapi.testclient import TestClient
from ai_server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data

def test_api_forecast():
    # Only test if model is loaded successfully
    health_res = client.get("/health").json()
    if health_res.get("model_loaded"):
        response = client.get("/api/forecast")
        assert response.status_code == 200
        data = response.json()
        assert "predicted_rps" in data
        assert data["predicted_rps"] >= 0
