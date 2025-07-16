import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def valid_metrics_data():
    return {
        "timestamp": "2023-10-01T12:00:00Z",
        "cpu_usage": 85,
        "memory_usage": 70,
        "latency_ms": 250,
        "disk_usage": 65,
        "network_in_kbps": 1200,
        "network_out_kbps": 900,
        "io_wait": 5,
        "thread_count": 150,
        "active_connections": 45,
        "error_rate": 0.02,
        "uptime_seconds": 360000,
        "temperature_celsius": 65,
        "power_consumption_watts": 250,
        "service_status": {
            "database": "online",
            "api_gateway": "degraded",
            "cache": "online"
        }
    }

def test_ingest_valid(valid_metrics_data):
    response = client.post("/api/ingest", json=valid_metrics_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert data["data"]["cpu_usage"] == 85

def test_ingest_missing_field(valid_metrics_data):
    del valid_metrics_data["cpu_usage"]
    response = client.post("/api/ingest", json=valid_metrics_data)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert any(e["field"] == "cpu_usage" for e in data["errors"])

def test_ingest_invalid_type(valid_metrics_data):
    valid_metrics_data["cpu_usage"] = "bad"
    response = client.post("/api/ingest", json=valid_metrics_data)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert any(e["field"] == "cpu_usage" for e in data["errors"])

def test_ingest_invalid_service_status(valid_metrics_data):
    valid_metrics_data["service_status"]["database"] = "bad"
    response = client.post("/api/ingest", json=valid_metrics_data)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert any("service_status.database" in e["field"] for e in data["errors"]) 