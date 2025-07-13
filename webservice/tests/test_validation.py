import pytest
from webservice.services.validation import ValidationService


@pytest.fixture
def validation_service():
    return ValidationService()


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


def test_validate_metrics_valid_data(validation_service, valid_metrics_data):
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.data is not None


def test_validate_metrics_missing_field(validation_service, valid_metrics_data):
    del valid_metrics_data["cpu_usage"]
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "cpu_usage"
    assert "missing" in result.errors[0].message


def test_validate_metrics_invalid_type(validation_service, valid_metrics_data):
    valid_metrics_data["cpu_usage"] = "85"
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "cpu_usage"
    assert "type" in result.errors[0].message


def test_validate_metrics_out_of_range(validation_service, valid_metrics_data):
    valid_metrics_data["cpu_usage"] = 150
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "cpu_usage"
    assert ">=" in result.errors[0].message or "<=" in result.errors[0].message


def test_validate_metrics_negative_value(validation_service, valid_metrics_data):
    valid_metrics_data["cpu_usage"] = -10
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "cpu_usage"


def test_validate_metrics_invalid_service_status(validation_service, valid_metrics_data):
    valid_metrics_data["service_status"]["database"] = "invalid_status"
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert "service_status.database" in result.errors[0].field


def test_validate_metrics_missing_service(validation_service, valid_metrics_data):
    del valid_metrics_data["service_status"]["database"]
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert "service_status.database" in result.errors[0].field


def test_validate_metrics_multiple_errors(validation_service, valid_metrics_data):
    valid_metrics_data["cpu_usage"] = 150
    valid_metrics_data["memory_usage"] = -5
    del valid_metrics_data["latency_ms"]
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) >= 3


def test_validate_metrics_not_dict(validation_service):
    result = validation_service.validate_metrics("not a dict")
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "root"


def test_validate_metrics_error_rate_float(validation_service, valid_metrics_data):
    valid_metrics_data["error_rate"] = 0.5
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is True


def test_validate_metrics_error_rate_out_of_range(validation_service, valid_metrics_data):
    valid_metrics_data["error_rate"] = 1.5
    
    result = validation_service.validate_metrics(valid_metrics_data)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "error_rate" 