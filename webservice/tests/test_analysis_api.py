import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from webservice.main import app
from webservice.models.analysis import AnalysisResult, Recommendation, RecommendationCategory

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


@pytest.fixture
def mock_analysis_result():
    return AnalysisResult(
        analysis_summary="System experiencing high resource usage",
        root_cause_analysis="CPU and memory pressure causing performance degradation",
        recommendations=[
            Recommendation(
                priority=1,
                category=RecommendationCategory.IMMEDIATE,
                action="Scale up CPU resources",
                impact="Reduce CPU usage by 30%",
                effort="low",
                technical_details="Add 2 more CPU cores"
            ),
            Recommendation(
                priority=2,
                category=RecommendationCategory.MONITORING,
                action="Set up resource monitoring alerts",
                impact="Early warning system",
                effort="medium"
            )
        ],
        confidence_score=0.85,
        analysis_metadata={
            "response_time": 1.2,
            "anomaly_count": 5,
            "critical_anomalies": 3
        }
    )


def test_analysis_no_metrics():
    response = client.get("/api/analysis")
    assert response.status_code == 404
    assert "No metrics available" in response.json()["detail"]


@patch('webservice.api.analysis.llm_service')
def test_analysis_with_normal_metrics(mock_llm_service, normal_metrics, mock_analysis_result):
    mock_llm_service.analyze_anomalies.return_value = mock_analysis_result
    
    client.post("/api/ingest", json=normal_metrics)
    
    response = client.get("/api/analysis")
    assert response.status_code == 200
    
    data = response.json()
    assert data["analysis_summary"] == "System experiencing high resource usage"
    assert data["confidence_score"] == 0.85
    assert len(data["recommendations"]) == 2
    
    rec1 = data["recommendations"][0]
    assert rec1["priority"] == 1
    assert rec1["category"] == "immediate"
    assert rec1["action"] == "Scale up CPU resources"


@patch('webservice.api.analysis.llm_service')
def test_analysis_with_anomalous_metrics(mock_llm_service, anomalous_metrics, mock_analysis_result):
    mock_llm_service.analyze_anomalies.return_value = mock_analysis_result
    
    client.post("/api/ingest", json=anomalous_metrics)
    
    response = client.get("/api/analysis")
    assert response.status_code == 200
    
    data = response.json()
    assert "analysis_summary" in data
    assert "root_cause_analysis" in data
    assert "recommendations" in data
    assert "confidence_score" in data
    assert "analysis_metadata" in data
    
    mock_llm_service.analyze_anomalies.assert_called_once()


@patch('webservice.api.analysis.llm_service')
def test_analysis_service_error(mock_llm_service, normal_metrics):
    mock_llm_service.analyze_anomalies.side_effect = Exception("LLM service error")
    
    client.post("/api/ingest", json=normal_metrics)
    
    response = client.get("/api/analysis")
    assert response.status_code == 500
    assert "Analysis failed" in response.json()["detail"]


@patch('webservice.api.analysis.llm_service')
def test_analysis_metrics_endpoint(mock_llm_service):
    mock_metrics = {
        "total_analyses": 5,
        "average_response_time": 1.5,
        "total_cost_estimate": 0.25,
        "last_analysis": "2023-10-01T12:00:00Z"
    }
    mock_llm_service.get_analysis_metrics.return_value = mock_metrics
    
    response = client.get("/api/analysis/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["total_analyses"] == 5
    assert data["data"]["average_response_time"] == 1.5


@patch('webservice.api.analysis.llm_service')
def test_analysis_metrics_error(mock_llm_service):
    mock_llm_service.get_analysis_metrics.side_effect = Exception("Metrics error")
    
    response = client.get("/api/analysis/metrics")
    assert response.status_code == 500
    assert "Failed to get analysis metrics" in response.json()["detail"]


def test_analysis_response_format(anomalous_metrics):
    with patch('webservice.api.analysis.llm_service') as mock_llm_service:
        mock_result = AnalysisResult(
            analysis_summary="Test summary",
            root_cause_analysis="Test root cause",
            recommendations=[],
            confidence_score=0.5,
            analysis_metadata={}
        )
        mock_llm_service.analyze_anomalies.return_value = mock_result
        
        client.post("/api/ingest", json=anomalous_metrics)
        
        response = client.get("/api/analysis")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["analysis_summary", "root_cause_analysis", "recommendations", "confidence_score", "analysis_metadata"]
        for field in required_fields:
            assert field in data 