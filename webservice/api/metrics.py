from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from webservice.services.validation import ValidationService
from webservice.models.metrics import InfrastructureMetrics
from webservice.models.validation import ValidationResult
import logging
import time
import os

router = APIRouter()
validation_service = ValidationService()
logger = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

latest_metrics = None

def get_latest_metrics():
    return latest_metrics

def set_latest_metrics(metrics):
    global latest_metrics
    latest_metrics = metrics

@router.post("/ingest", status_code=200)
async def ingest_metrics(request: Request):
    start_time = time.time()
    
    try:
        data = await request.json()
        logger.info("Metrics ingestion request received")
        
        if DEBUG:
            logger.debug(f"Processing metrics validation...")
        
        validation_start = time.time()
        result: ValidationResult = validation_service.validate_metrics(data)
        validation_time = time.time() - validation_start
        
        if DEBUG:
            logger.debug(f"Validation completed in {validation_time:.3f}s")
        
        if not result.is_valid:
            logger.warning(f"Validation failed with {len(result.errors)} errors")
            if DEBUG:
                for error in result.errors:
                    logger.error(f"Validation error | field: {error.field} | value: {error.value} | message: {error.message}")
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "errors": [e.model_dump() for e in result.errors]
                }
            )
        
        set_latest_metrics(result.data)
        
        total_time = time.time() - start_time
        logger.info(f"Metrics ingestion successful in {total_time:.3f}s")
        
        if DEBUG:
            logger.debug(f"Latest metrics updated: CPU={latest_metrics.get('cpu_usage')}%, Memory={latest_metrics.get('memory_usage')}%, Latency={latest_metrics.get('latency_ms')}ms")
        
        return {
            "status": "success",
            "data": latest_metrics
        }
        
    except Exception as e:
        logger.error(f"Error during metrics ingestion: {str(e)}")
        if DEBUG:
            logger.debug(f"Full error details:", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        ) 