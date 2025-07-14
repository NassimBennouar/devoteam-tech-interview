from fastapi import APIRouter, HTTPException, Depends
from webservice.services.anomaly_detection import AnomalyDetectionService
from webservice.models.anomaly import AnomalyResult
from webservice.api.metrics import get_latest_metrics_from_db
from webservice.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import os

router = APIRouter()
anomaly_service = AnomalyDetectionService()
logger = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


@router.get("/anomalies", response_model=AnomalyResult)
async def get_anomalies(session: AsyncSession = Depends(get_async_session)):
    if DEBUG:
        logger.debug("Anomalies endpoint called")
    
    latest_metrics = await get_latest_metrics_from_db(session)
    if latest_metrics is None:
        if DEBUG:
            logger.debug("No metrics available for anomaly detection")
        raise HTTPException(
            status_code=404,
            detail="No metrics available. Please ingest metrics first using POST /api/ingest"
        )
    
    logger.info("Analyzing metrics for anomalies")
    result = anomaly_service.detect_anomalies(latest_metrics)
    
    if DEBUG:
        logger.debug(f"Anomaly detection result: {result.summary}")
        for anomaly in result.anomalies:
            logger.debug(f"Anomaly: {anomaly.metric} = {anomaly.value} (severity {anomaly.severity})")
    
    logger.info(f"Anomaly detection completed: {result.summary}")
    return result


@router.get("/anomalies/history")
async def get_anomaly_history():
    if DEBUG:
        logger.debug("Anomaly history endpoint called")
    
    history = anomaly_service.get_history_summary()
    
    if DEBUG:
        logger.debug(f"History summary: {history}")
    
    return {
        "status": "success",
        "data": history
    } 