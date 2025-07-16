import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def normal_metrics():
    return {
        "timestamp": "2023-10-01T12:00:00Z",
        "cpu_usage": 50,
        "memory_usage": 60,
        "latency_ms": 100,
        "disk_usage": 70,
        "network_in_kbps": 1000,
        "network_out_kbps": 800,
        "io_wait": 3,
        "thread_count": 100,
        "active_connections": 50,
        "error_rate": 0.01,
        "uptime_seconds": 7200,
        "temperature_celsius": 65,
        "power_consumption_watts": 250,
        "service_status": {
            "database": "online",
            "api_gateway": "online",
            "cache": "online"
        }
    }

@pytest.fixture
def anomalous_metrics():
    return {
        "timestamp": "2023-10-01T12:00:00Z",
        "cpu_usage": 95,
        "memory_usage": 90,
        "latency_ms": 600,
        "disk_usage": 95,
        "network_in_kbps": 1000,
        "network_out_kbps": 800,
        "io_wait": 15,
        "thread_count": 100,
        "active_connections": 200,
        "error_rate": 0.08,
        "uptime_seconds": 1800,
        "temperature_celsius": 85,
        "power_consumption_watts": 450,
        "service_status": {
            "database": "offline",
            "api_gateway": "degraded",
            "cache": "online"
        }
    }

def test_anomalies_no_metrics():
    response = client.get("/api/anomalies")
    assert response.status_code == 404
    assert "No metrics available" in response.json()["detail"]

def test_anomalies_normal_metrics(normal_metrics):
    client.post("/api/ingest", json=normal_metrics)
    
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    
    data = response.json()
    assert data["has_anomalies"] is False
    assert len(data["anomalies"]) == 0
    assert data["total_count"] == 0
    assert "No anomalies detected" in data["summary"]

def test_anomalies_with_anomalous_metrics(anomalous_metrics):
    client.post("/api/ingest", json=anomalous_metrics)
    
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    
    data = response.json()
    assert data["has_anomalies"] is True
    assert len(data["anomalies"]) > 0
    assert data["total_count"] > 0
    assert "anomalies detected" in data["summary"]
    
    cpu_anomaly = next((a for a in data["anomalies"] if a["metric"] == "cpu_usage"), None)
    assert cpu_anomaly is not None
    assert cpu_anomaly["severity"] == 5
    assert cpu_anomaly["type"] == "performance"

def test_anomalies_service_status(anomalous_metrics):
    client.post("/api/ingest", json=anomalous_metrics)
    
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    
    data = response.json()
    
    offline_anomaly = next((a for a in data["anomalies"] if a["metric"] == "service_status.database"), None)
    assert offline_anomaly is not None
    assert offline_anomaly["severity"] == 5
    assert offline_anomaly["value"] == "offline"
    
    degraded_anomaly = next((a for a in data["anomalies"] if a["metric"] == "service_status.api_gateway"), None)
    assert degraded_anomaly is not None
    assert degraded_anomaly["severity"] == 3
    assert degraded_anomaly["value"] == "degraded"

def test_anomalies_history_endpoint():
    response = client.get("/api/anomalies/history")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "network_in_kbps" in data["data"]
    assert "network_out_kbps" in data["data"]
    assert "thread_count" in data["data"]

def test_anomalies_history_after_ingestion(normal_metrics):
    client.post("/api/ingest", json=normal_metrics)
    client.get("/api/anomalies")
    
    response = client.get("/api/anomalies/history")
    assert response.status_code == 200
    
    data = response.json()
    history = data["data"]
    
    for metric in ["network_in_kbps", "network_out_kbps", "thread_count"]:
        assert history[metric]["count"] > 0
        assert len(history[metric]["values"]) > 0
        assert history[metric]["average"] is not None

def test_anomalies_response_format(anomalous_metrics):
    client.post("/api/ingest", json=anomalous_metrics)
    
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    
    data = response.json()
    
    required_fields = ["has_anomalies", "anomalies", "summary", "total_count"]
    for field in required_fields:
        assert field in data
    
    if data["anomalies"]:
        anomaly = data["anomalies"][0]
        anomaly_fields = ["metric", "value", "severity", "type", "message"]
        for field in anomaly_fields:
            assert field in anomaly 