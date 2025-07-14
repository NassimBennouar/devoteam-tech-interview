from pydantic import BaseModel
from typing import List, Optional, Any
from enum import Enum


class AnomalyType(str, Enum):
    PERFORMANCE = "performance"
    CAPACITY = "capacity"
    HEALTH = "health"
    STABILITY = "stability"


class Anomaly(BaseModel):
    metric: str
    value: Any
    threshold: Optional[Any] = None
    severity: int
    type: AnomalyType
    message: str


class AnomalyResult(BaseModel):
    has_anomalies: bool
    anomalies: List[Anomaly] = []
    summary: str
    total_count: int 