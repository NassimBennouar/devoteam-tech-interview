from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class ServiceStatus(BaseModel):
    database: str = Field(..., description="Database service status")
    api_gateway: str = Field(..., description="API Gateway service status")
    cache: str = Field(..., description="Cache service status")


class InfrastructureMetrics(BaseModel):
    timestamp: str = Field(..., description="Timestamp of the metrics")
    cpu_usage: int = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: int = Field(..., ge=0, le=100, description="Memory usage percentage")
    latency_ms: int = Field(..., gt=0, description="Latency in milliseconds")
    disk_usage: int = Field(..., ge=0, le=100, description="Disk usage percentage")
    network_in_kbps: int = Field(..., gt=0, description="Network input in Kbps")
    network_out_kbps: int = Field(..., gt=0, description="Network output in Kbps")
    io_wait: int = Field(..., ge=0, description="IO wait time")
    thread_count: int = Field(..., gt=0, description="Number of threads")
    active_connections: int = Field(..., ge=0, description="Number of active connections")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate (0-1)")
    uptime_seconds: int = Field(..., gt=0, description="Uptime in seconds")
    temperature_celsius: int = Field(..., description="Temperature in Celsius")
    power_consumption_watts: int = Field(..., gt=0, description="Power consumption in Watts")
    service_status: ServiceStatus = Field(..., description="Services status")


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []
    data: Optional[InfrastructureMetrics] = None


class ApiResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None 