import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
import importlib
import sys

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

def test_debug_mode_enabled():
    with patch.dict(os.environ, {"DEBUG": "true"}):
        if 'webservice.main' in sys.modules:
            del sys.modules['webservice.main']
        from main import DEBUG
        assert DEBUG is True

def test_debug_mode_disabled():
    with patch.dict(os.environ, {"DEBUG": "false"}):
        if 'webservice.main' in sys.modules:
            del sys.modules['webservice.main']
        from main import DEBUG
        assert DEBUG is False

def test_debug_mode_default():
    with patch.dict(os.environ, {}, clear=True):
        if 'webservice.main' in sys.modules:
            del sys.modules['webservice.main']
        from main import DEBUG
        assert DEBUG is False

def test_ingest_with_debug_timing(valid_metrics_data, caplog):
    with patch.dict(os.environ, {"DEBUG": "true"}):
        if 'webservice.main' in sys.modules:
            del sys.modules['webservice.main']
        if 'webservice.api.metrics' in sys.modules:
            del sys.modules['webservice.api.metrics']
        
        from main import app
        client = TestClient(app)
        
        with caplog.at_level("DEBUG"):
            response = client.post("/api/ingest", json=valid_metrics_data)
            assert response.status_code == 200
            assert "Validation completed in" in caplog.text

def test_ingest_basic_logging(valid_metrics_data, caplog):
    with patch.dict(os.environ, {"DEBUG": "false"}):
        if 'webservice.main' in sys.modules:
            del sys.modules['webservice.main']
        if 'webservice.api.metrics' in sys.modules:
            del sys.modules['webservice.api.metrics']
        
        from main import app
        client = TestClient(app)
        
        with caplog.at_level("INFO"):
            response = client.post("/api/ingest", json=valid_metrics_data)
            assert response.status_code == 200
            assert "Metrics ingestion successful" in caplog.text 