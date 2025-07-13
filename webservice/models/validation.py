from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ValidationError(BaseModel):
    field: str
    message: str
    value: Optional[Any] = None


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError] = []
    data: Optional[Dict[str, Any]] = None 