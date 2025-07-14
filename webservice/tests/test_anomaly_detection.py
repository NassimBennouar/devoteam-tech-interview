import pytest
from webservice.services.anomaly_detection import AnomalyDetectionService
from webservice.models.anomaly import AnomalyType


@pytest.fixture
def anomaly_service():
    return AnomalyDetectionService()


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


def test_no_anomalies_normal_metrics(anomaly_service, normal_metrics):
    result = anomaly_service.detect_anomalies(normal_metrics)
    
    assert result.has_anomalies is False
    assert len(result.anomalies) == 0
    assert result.total_count == 0
    assert "No anomalies detected" in result.summary


def test_critical_anomalies_detection(anomaly_service, anomalous_metrics):
    result = anomaly_service.detect_anomalies(anomalous_metrics)
    
    assert result.has_anomalies is True
    assert result.total_count > 0
    
    critical_anomalies = [a for a in result.anomalies if a.severity == 5]
    assert len(critical_anomalies) > 0
    
    cpu_anomaly = next((a for a in result.anomalies if a.metric == "cpu_usage"), None)
    assert cpu_anomaly is not None
    assert cpu_anomaly.severity == 5
    assert cpu_anomaly.type == AnomalyType.PERFORMANCE


def test_service_status_anomalies(anomaly_service, anomalous_metrics):
    result = anomaly_service.detect_anomalies(anomalous_metrics)
    
    offline_anomaly = next((a for a in result.anomalies if a.metric == "service_status.database"), None)
    assert offline_anomaly is not None
    assert offline_anomaly.severity == 5
    assert offline_anomaly.type == AnomalyType.STABILITY
    
    degraded_anomaly = next((a for a in result.anomalies if a.metric == "service_status.api_gateway"), None)
    assert degraded_anomaly is not None
    assert degraded_anomaly.severity == 3
    assert degraded_anomaly.type == AnomalyType.STABILITY


def test_uptime_anomaly(anomaly_service, anomalous_metrics):
    result = anomaly_service.detect_anomalies(anomalous_metrics)
    
    uptime_anomaly = next((a for a in result.anomalies if a.metric == "uptime_seconds"), None)
    assert uptime_anomaly is not None
    assert uptime_anomaly.severity == 3
    assert uptime_anomaly.type == AnomalyType.STABILITY


def test_relative_threshold_no_history(anomaly_service, normal_metrics):
    result = anomaly_service.detect_anomalies(normal_metrics)
    
    network_anomalies = [a for a in result.anomalies if "network" in a.metric]
    thread_anomalies = [a for a in result.anomalies if a.metric == "thread_count"]
    
    assert len(network_anomalies) == 0
    assert len(thread_anomalies) == 0


def test_relative_threshold_with_history(anomaly_service, normal_metrics):
    for _ in range(3):
        anomaly_service.detect_anomalies(normal_metrics)
    
    high_network_metrics = normal_metrics.copy()
    high_network_metrics["network_in_kbps"] = 3000
    
    result = anomaly_service.detect_anomalies(high_network_metrics)
    
    network_anomaly = next((a for a in result.anomalies if a.metric == "network_in_kbps"), None)
    assert network_anomaly is not None
    assert network_anomaly.severity >= 3


def test_warning_vs_critical_thresholds(anomaly_service):
    warning_metrics = {
        "cpu_usage": 85,
        "memory_usage": 82,
        "latency_ms": 300,
        "disk_usage": 85,
        "io_wait": 7,
        "error_rate": 0.03,
        "temperature_celsius": 75,
        "power_consumption_watts": 350,
        "active_connections": 120,
        "uptime_seconds": 7200,
        "service_status": {"database": "online", "api_gateway": "online", "cache": "online"}
    }
    
    result = anomaly_service.detect_anomalies(warning_metrics)
    
    warning_anomalies = [a for a in result.anomalies if a.severity == 3]
    critical_anomalies = [a for a in result.anomalies if a.severity == 5]
    
    assert len(warning_anomalies) > 0
    assert len(critical_anomalies) == 0


def test_history_update(anomaly_service, normal_metrics):
    initial_history = anomaly_service.get_history_summary()
    
    for metric in ["network_in_kbps", "network_out_kbps", "thread_count"]:
        assert initial_history[metric]["count"] == 0
    
    anomaly_service.detect_anomalies(normal_metrics)
    
    updated_history = anomaly_service.get_history_summary()
    
    for metric in ["network_in_kbps", "network_out_kbps", "thread_count"]:
        assert updated_history[metric]["count"] == 1
        assert updated_history[metric]["values"][0] == normal_metrics[metric]


def test_anomaly_types_classification(anomaly_service, anomalous_metrics):
    result = anomaly_service.detect_anomalies(anomalous_metrics)
    
    performance_anomalies = [a for a in result.anomalies if a.type == AnomalyType.PERFORMANCE]
    capacity_anomalies = [a for a in result.anomalies if a.type == AnomalyType.CAPACITY]
    health_anomalies = [a for a in result.anomalies if a.type == AnomalyType.HEALTH]
    stability_anomalies = [a for a in result.anomalies if a.type == AnomalyType.STABILITY]
    
    assert len(performance_anomalies) > 0
    assert len(capacity_anomalies) > 0
    assert len(health_anomalies) > 0
    assert len(stability_anomalies) > 0


def test_summary_format(anomaly_service, anomalous_metrics):
    result = anomaly_service.detect_anomalies(anomalous_metrics)
    
    assert "anomalies detected" in result.summary
    assert "critical" in result.summary
    assert "warning" in result.summary
    assert result.total_count == len(result.anomalies) 