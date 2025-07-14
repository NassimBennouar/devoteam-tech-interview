from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse
from webservice.services.validation import ValidationService
from webservice.services.persistence import PersistenceService
from webservice.models.metrics import InfrastructureMetrics
from webservice.models.validation import ValidationResult
from webservice.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time
import os
from typing import List, Dict, Any

router = APIRouter()
validation_service = ValidationService()
persistence_service = PersistenceService()
logger = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

latest_metrics = None

def get_latest_metrics():
    return latest_metrics

def set_latest_metrics(metrics):
    global latest_metrics
    latest_metrics = metrics

@router.post("/ingest", status_code=200)
async def ingest_metrics(request: Request, session: AsyncSession = Depends(get_async_session)):
    start_time = time.time()
    
    try:
        data = await request.json()
        logger.info("Metrics ingestion request received")
        
        if isinstance(data, dict):
            return await _process_single_metrics(data, session, start_time)
        elif isinstance(data, list):
            return await _process_batch_metrics(data, session, start_time)
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "message": "Data must be a dictionary (single metrics) or list of dictionaries (batch)"
                }
            )
        
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

async def _process_single_metrics(data: Dict[str, Any], session: AsyncSession, start_time: float):
    if DEBUG:
        logger.debug(f"Processing single metrics validation...")
    
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
    
    storage_start = time.time()
    storage_success = await persistence_service.store_metrics(session, result.data)
    storage_time = time.time() - storage_start
    
    if not storage_success:
        logger.error("Failed to store metrics in database")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to store metrics"
            }
        )
    
    set_latest_metrics(result.data)
    
    total_time = time.time() - start_time
    logger.info(f"Single metrics ingestion successful in {total_time:.3f}s (validation: {validation_time:.3f}s, storage: {storage_time:.3f}s)")
    
    if DEBUG:
        logger.debug(f"Latest metrics updated: CPU={latest_metrics.get('cpu_usage')}%, Memory={latest_metrics.get('memory_usage')}%, Latency={latest_metrics.get('latency_ms')}ms")
    
    return {
        "status": "success",
        "data": latest_metrics,
        "processing_time": total_time
    }

async def _process_batch_metrics(data: List[Dict[str, Any]], session: AsyncSession, start_time: float):
    logger.info(f"Processing batch of {len(data)} metrics")
    
    if DEBUG:
        logger.debug(f"Processing batch validation and storage...")
    
    batch_start = time.time()
    result = await persistence_service.store_metrics_batch(session, data)
    batch_time = time.time() - batch_start
    
    total_time = time.time() - start_time
    logger.info(f"Batch processing completed in {total_time:.3f}s: {result['stored']} stored, {result['failed']} failed")
    
    if result['stored'] == 0:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "No valid metrics found in batch",
                "batch_result": result
            }
        )
    
    return {
        "status": "success",
        "batch_result": result,
        "processing_time": total_time
    } 