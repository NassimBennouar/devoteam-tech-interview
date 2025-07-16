import pytest
from services.anomaly_detection import AnomalyDetectionService
from models.anomaly import AnomalyType


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


def test_analyze_historical_anomalies(anomaly_service):
    """Test historical anomaly analysis"""
    # Create test metrics with different anomaly patterns
    metrics_list = [
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "cpu_usage": 95,  # Critical
            "memory_usage": 85,  # Critical
            "latency_ms": 100,  # Normal
            "disk_usage": 70,  # Normal
            "network_in_kbps": 500,
            "network_out_kbps": 400,
            "io_wait": 2,
            "thread_count": 50,
            "active_connections": 80,
            "error_rate": 0.01,
            "uptime_seconds": 7200,
            "temperature_celsius": 65,
            "power_consumption_watts": 250,
            "service_status": {"database": "online", "api_gateway": "online", "cache": "online"}
        },
        {
            "timestamp": "2024-01-01T11:00:00Z",
            "cpu_usage": 75,  # Normal
            "memory_usage": 90,  # Critical
            "latency_ms": 600,  # Critical
            "disk_usage": 70,  # Normal
            "network_in_kbps": 500,
            "network_out_kbps": 400,
            "io_wait": 2,
            "thread_count": 50,
            "active_connections": 80,
            "error_rate": 0.01,
            "uptime_seconds": 7200,
            "temperature_celsius": 65,
            "power_consumption_watts": 250,
            "service_status": {"database": "online", "api_gateway": "degraded", "cache": "online"}
        },
        {
            "timestamp": "2024-01-01T12:00:00Z",
            "cpu_usage": 70,  # Normal
            "memory_usage": 75,  # Normal
            "latency_ms": 150,  # Normal
            "disk_usage": 70,  # Normal
            "network_in_kbps": 500,
            "network_out_kbps": 400,
            "io_wait": 2,
            "thread_count": 50,
            "active_connections": 80,
            "error_rate": 0.01,
            "uptime_seconds": 7200,
            "temperature_celsius": 65,
            "power_consumption_watts": 250,
            "service_status": {"database": "online", "api_gateway": "online", "cache": "online"}
        }
    ]
    
    analyzed_timeline = anomaly_service.analyze_historical_anomalies(metrics_list)
    
    # Verify structure
    assert len(analyzed_timeline) == 3
    
    # Check first point (should have CPU and memory anomalies)
    first_point = analyzed_timeline[0]
    assert first_point["timestamp"] == "2024-01-01T10:00:00Z"
    assert first_point["has_issues"] == True
    assert first_point["total_count"] == 2  # CPU + Memory
    
    # Check second point (should have memory, latency, and service anomalies)
    second_point = analyzed_timeline[1]
    assert second_point["has_issues"] == True
    assert second_point["total_count"] == 3  # Memory + Latency + Service
    
    # Check third point (should have no anomalies)
    third_point = analyzed_timeline[2]
    assert third_point["has_issues"] == False
    assert third_point["total_count"] == 0


def test_analyze_anomaly_patterns(anomaly_service):
    """Test anomaly pattern analysis"""
    # Create analyzed timeline with known patterns
    analyzed_timeline = [
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "anomalies": [
                {"metric": "cpu_usage", "severity": 5, "value": 95},
                {"metric": "memory_usage", "severity": 5, "value": 85}
            ],
            "has_issues": True,
            "total_count": 2
        },
        {
            "timestamp": "2024-01-01T11:00:00Z",
            "anomalies": [
                {"metric": "cpu_usage", "severity": 3, "value": 85},
                {"metric": "latency_ms", "severity": 5, "value": 600}
            ],
            "has_issues": True,
            "total_count": 2
        },
        {
            "timestamp": "2024-01-01T17:00:00Z",
            "anomalies": [
                {"metric": "cpu_usage", "severity": 5, "value": 95},
                {"metric": "latency_ms", "severity": 3, "value": 300}
            ],
            "has_issues": True,
            "total_count": 2
        }
    ]
    
    patterns = anomaly_service.analyze_anomaly_patterns(analyzed_timeline)
    
    # Verify structure
    assert "frequency" in patterns
    assert "temporal" in patterns
    assert "cooccurrence" in patterns
    assert patterns["total_points"] == 3
    
    # Check frequency analysis
    frequency = patterns["frequency"]
    assert frequency["counts"]["cpu_usage"] == 3  # CPU appears in all 3 points
    assert frequency["counts"]["memory_usage"] == 1  # Memory appears in 1 point
    assert frequency["counts"]["latency_ms"] == 2  # Latency appears in 2 points
    
    # Check most frequent
    assert frequency["most_frequent"][0] == "cpu_usage"
    assert frequency["most_frequent"][1] == 3
    
    # Check severity averages
    assert abs(frequency["severity_avg"]["cpu_usage"] - (5 + 3 + 5) / 3) < 0.01
    
    # Check temporal patterns
    temporal = patterns["temporal"]
    assert "hourly_distribution" in temporal
    assert "problematic_hours" in temporal
    assert "peak_hour" in temporal
    
    # Check co-occurrence
    cooccurrence = patterns["cooccurrence"]
    assert "pairs" in cooccurrence
    assert "most_common" in cooccurrence
    
    # CPU and latency should co-occur twice
    cpu_latency_pair = tuple(sorted(["cpu_usage", "latency_ms"]))
    assert cooccurrence["pairs"][cpu_latency_pair] == 2


def test_analyze_frequency(anomaly_service):
    """Test frequency analysis"""
    analyzed_timeline = [
        {
            "anomalies": [
                {"metric": "cpu_usage", "severity": 5},
                {"metric": "memory_usage", "severity": 3}
            ]
        },
        {
            "anomalies": [
                {"metric": "cpu_usage", "severity": 3}
            ]
        }
    ]
    
    frequency = anomaly_service._analyze_frequency(analyzed_timeline)
    
    assert frequency["counts"]["cpu_usage"] == 2
    assert frequency["counts"]["memory_usage"] == 1
    assert frequency["most_frequent"] == ("cpu_usage", 2)
    assert frequency["severity_avg"]["cpu_usage"] == 4.0  # (5 + 3) / 2
    assert frequency["severity_avg"]["memory_usage"] == 3.0


def test_analyze_temporal_patterns(anomaly_service):
    """Test temporal pattern analysis"""
    analyzed_timeline = [
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "total_count": 2
        },
        {
            "timestamp": "2024-01-01T10:30:00Z",
            "total_count": 1
        },
        {
            "timestamp": "2024-01-01T17:00:00Z",
            "total_count": 3
        },
        {
            "timestamp": "2024-01-01T17:30:00Z",
            "total_count": 2
        }
    ]
    
    temporal = anomaly_service._analyze_temporal_patterns(analyzed_timeline)
    
    assert "hourly_distribution" in temporal
    assert "problematic_hours" in temporal
    assert "peak_hour" in temporal
    
    # Hour 10 should have average of (2 + 1) / 2 = 1.5
    assert temporal["hourly_distribution"][10] == 1.5
    
    # Hour 17 should have average of (3 + 2) / 2 = 2.5
    assert temporal["hourly_distribution"][17] == 2.5
    
    # Peak hour should be 17
    assert temporal["peak_hour"][0] == 17
    assert temporal["peak_hour"][1] == 2.5


def test_analyze_cooccurrence(anomaly_service):
    """Test co-occurrence analysis"""
    analyzed_timeline = [
        {
            "anomalies": [
                {"metric": "cpu_usage"},
                {"metric": "memory_usage"},
                {"metric": "latency_ms"}
            ]
        },
        {
            "anomalies": [
                {"metric": "cpu_usage"},
                {"metric": "latency_ms"}
            ]
        },
        {
            "anomalies": [
                {"metric": "disk_usage"}
            ]
        }
    ]
    
    cooccurrence = anomaly_service._analyze_cooccurrence(analyzed_timeline)
    
    # Check pairs
    cpu_memory_pair = tuple(sorted(["cpu_usage", "memory_usage"]))
    cpu_latency_pair = tuple(sorted(["cpu_usage", "latency_ms"]))
    memory_latency_pair = tuple(sorted(["memory_usage", "latency_ms"]))
    
    assert cooccurrence["pairs"][cpu_memory_pair] == 1
    assert cooccurrence["pairs"][cpu_latency_pair] == 2
    assert cooccurrence["pairs"][memory_latency_pair] == 1
    
    # Check most common
    assert cooccurrence["most_common"][0] == (cpu_latency_pair, 2)
    assert cooccurrence["total_pairs"] == 3


def test_historical_analysis_empty_data(anomaly_service):
    """Test historical analysis with empty data"""
    analyzed_timeline = anomaly_service.analyze_historical_anomalies([])
    assert len(analyzed_timeline) == 0
    
    patterns = anomaly_service.analyze_anomaly_patterns([])
    assert patterns["total_points"] == 0
    assert patterns["frequency"]["counts"] == {}
    assert patterns["temporal"]["hourly_distribution"] == {}
    assert patterns["cooccurrence"]["pairs"] == {}


def test_historical_analysis_no_anomalies(anomaly_service):
    """Test historical analysis with no anomalies"""
    metrics_list = [
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "cpu_usage": 50,  # Normal
            "memory_usage": 60,  # Normal
            "latency_ms": 100,  # Normal
            "disk_usage": 70,  # Normal
            "network_in_kbps": 500,
            "network_out_kbps": 400,
            "io_wait": 2,
            "thread_count": 50,
            "active_connections": 80,
            "error_rate": 0.01,
            "uptime_seconds": 7200,
            "temperature_celsius": 65,
            "power_consumption_watts": 250,
            "service_status": {"database": "online", "api_gateway": "online", "cache": "online"}
        }
    ]
    
    analyzed_timeline = anomaly_service.analyze_historical_anomalies(metrics_list)
    patterns = anomaly_service.analyze_anomaly_patterns(analyzed_timeline)
    
    assert len(analyzed_timeline) == 1
    assert analyzed_timeline[0]["has_issues"] == False
    assert patterns["frequency"]["counts"] == {}
    assert patterns["frequency"]["most_frequent"] is None 