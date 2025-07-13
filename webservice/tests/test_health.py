import pytest
from fastapi.testclient import TestClient
from webservice.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["message"] == "Infrastructure Monitoring API is running"
    assert "timestamp" in data["data"]
    assert data["data"]["version"] == "0.1.0"


def test_health_check_response_format():
    response = client.get("/api/health")
    data = response.json()
    
    assert "status" in data
    assert "message" in data
    assert "data" in data
    
    assert isinstance(data["status"], str)
    assert isinstance(data["message"], str)
    assert isinstance(data["data"], dict) 