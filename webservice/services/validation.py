from typing import Dict, Any, List
import logging
from models.validation import ValidationResult, ValidationError
from models.metrics import InfrastructureMetrics

logger = logging.getLogger(__name__)


class ValidationService:
    def __init__(self):
        self.required_fields = [
            "timestamp", "cpu_usage", "memory_usage", "latency_ms", 
            "disk_usage", "network_in_kbps", "network_out_kbps", 
            "io_wait", "thread_count", "active_connections", 
            "error_rate", "uptime_seconds", "temperature_celsius", 
            "power_consumption_watts", "service_status"
        ]
        
        self.field_validations = {
            "cpu_usage": {"type": int, "min": 0, "max": 100},
            "memory_usage": {"type": int, "min": 0, "max": 100},
            "latency_ms": {"type": int, "min": 1},
            "disk_usage": {"type": int, "min": 0, "max": 100},
            "network_in_kbps": {"type": int, "min": 0},
            "network_out_kbps": {"type": int, "min": 0},
            "io_wait": {"type": int, "min": 0, "max": 100},
            "thread_count": {"type": int, "min": 0},
            "active_connections": {"type": int, "min": 0},
            "error_rate": {"type": float, "min": 0.0, "max": 1.0},
            "uptime_seconds": {"type": int, "min": 0},
            "temperature_celsius": {"type": int, "min": 0, "max": 200},
            "power_consumption_watts": {"type": int, "min": 0},
        }

    def validate_metrics(self, data: Dict[str, Any]) -> ValidationResult:
        errors = []
        
        if not isinstance(data, dict):
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(field="root", message="Data must be a dictionary")]
            )

        for field in self.required_fields:
            if field not in data:
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing"
                ))
                continue

            if field in self.field_validations:
                field_errors = self._validate_field(field, data[field])
                errors.extend(field_errors)

        service_status_errors = self._validate_service_status(data.get("service_status", {}))
        errors.extend(service_status_errors)

        is_valid = len(errors) == 0
        
        if is_valid:
            try:
                validated_data = InfrastructureMetrics(**data)
                return ValidationResult(is_valid=True, data=validated_data.model_dump())
            except Exception as e:
                errors.append(ValidationError(
                    field="pydantic_validation",
                    message=f"Pydantic validation failed: {str(e)}"
                ))
                is_valid = False

        return ValidationResult(is_valid=is_valid, errors=errors)

    def _validate_field(self, field: str, value: Any) -> List[ValidationError]:
        errors = []
        validation = self.field_validations[field]
        
        if not isinstance(value, validation["type"]):
            errors.append(ValidationError(
                field=field,
                message=f"Field '{field}' must be of type {validation['type'].__name__}",
                value=value
            ))
            return errors

        if "min" in validation and value < validation["min"]:
            errors.append(ValidationError(
                field=field,
                message=f"Field '{field}' must be >= {validation['min']}",
                value=value
            ))

        if "max" in validation and value > validation["max"]:
            errors.append(ValidationError(
                field=field,
                message=f"Field '{field}' must be <= {validation['max']}",
                value=value
            ))

        return errors

    def _validate_service_status(self, service_status: Any) -> List[ValidationError]:
        errors = []
        
        if not isinstance(service_status, dict):
            errors.append(ValidationError(
                field="service_status",
                message="Service status must be a dictionary",
                value=service_status
            ))
            return errors

        required_services = ["database", "api_gateway", "cache"]
        valid_statuses = ["online", "degraded", "offline"]

        for service in required_services:
            if service not in service_status:
                errors.append(ValidationError(
                    field=f"service_status.{service}",
                    message=f"Required service '{service}' is missing"
                ))
            elif service_status[service] not in valid_statuses:
                errors.append(ValidationError(
                    field=f"service_status.{service}",
                    message=f"Service status must be one of {valid_statuses}",
                    value=service_status[service]
                ))

        return errors 