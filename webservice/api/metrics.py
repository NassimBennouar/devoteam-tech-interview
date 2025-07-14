from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from webservice.services.validation import ValidationService
from webservice.models.metrics import InfrastructureMetrics
from webservice.models.validation import ValidationResult

router = APIRouter()
validation_service = ValidationService()

latest_metrics = None

@router.post("/ingest", status_code=200)
async def ingest_metrics(request: Request):
    data = await request.json()
    result: ValidationResult = validation_service.validate_metrics(data)
    if not result.is_valid:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "errors": [e.model_dump() for e in result.errors]
            }
        )
    global latest_metrics
    latest_metrics = result.data
    return {
        "status": "success",
        "data": latest_metrics
    } 