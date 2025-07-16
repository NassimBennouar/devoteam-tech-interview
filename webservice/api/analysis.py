from fastapi import APIRouter, HTTPException, Depends, Query
from services.llm_analysis import LLMAnalysisService
from services.anomaly_detection import AnomalyDetectionService
from services.metrics_service import MetricsService
from models.analysis import AnalysisResult
from db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
import os

router = APIRouter()
llm_service = LLMAnalysisService()
anomaly_service = AnomalyDetectionService()
metrics_service = MetricsService()
logger = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


@router.get("/analysis", response_model=AnalysisResult)
async def get_analysis(session: AsyncSession = Depends(get_async_session)):
    if DEBUG:
        logger.debug("Analysis endpoint called")
    
    latest_metrics = await metrics_service.get_latest_metrics(session)
    if latest_metrics is None:
        if DEBUG:
            logger.debug("No metrics available for analysis")
        raise HTTPException(
            status_code=404,
            detail="No metrics available. Please ingest metrics first using POST /api/ingest"
        )
    
    try:
        logger.info("Starting comprehensive analysis")
        
        anomaly_result = anomaly_service.detect_anomalies(latest_metrics)
        
        history_summary = anomaly_service.get_history_summary()
        
        if DEBUG:
            logger.debug(f"Anomaly detection found {anomaly_result.total_count} anomalies")
            logger.debug(f"History summary: {history_summary}")
        
        analysis_result = llm_service.analyze_anomalies(
            anomaly_result=anomaly_result,
            metrics=latest_metrics,
            history_summary=history_summary
        )
        
        logger.info(f"Analysis completed with {len(analysis_result.recommendations)} recommendations")
        
        if DEBUG:
            logger.debug(f"Analysis confidence: {analysis_result.confidence_score}")
            for rec in analysis_result.recommendations:
                logger.debug(f"Recommendation: {rec.priority} - {rec.action}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        if DEBUG:
            logger.debug("Full error details:", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/analysis/historical", response_model=AnalysisResult)
async def get_historical_analysis(
    points: Optional[int] = Query(50, description="Number of historical points to analyze", ge=10, le=200),
    session: AsyncSession = Depends(get_async_session)
):
    if DEBUG:
        logger.debug(f"Historical analysis endpoint called with {points} points")
    
    try:
        historical_metrics = await metrics_service.get_historical_metrics(session, points)
        
        if len(historical_metrics) < 10:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient historical data. Need at least 10 points, found {len(historical_metrics)}. Please ingest more metrics first."
            )
        
        logger.info(f"Starting historical analysis with {len(historical_metrics)} points")
        
        analysis_result = llm_service.analyze_historical_data(historical_metrics, anomaly_service)
        
        logger.info(f"Historical analysis completed with {len(analysis_result.recommendations)} recommendations")
        
        if DEBUG:
            logger.debug(f"Historical analysis confidence: {analysis_result.confidence_score}")
            logger.debug(f"Analysis metadata: {analysis_result.analysis_metadata}")
            for rec in analysis_result.recommendations:
                logger.debug(f"Historical recommendation: {rec.priority} - {rec.action}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during historical analysis: {str(e)}")
        if DEBUG:
            logger.debug("Full error details:", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Historical analysis failed: {str(e)}"
        )


@router.get("/analysis/metrics")
async def get_analysis_metrics():
    if DEBUG:
        logger.debug("Analysis metrics endpoint called")
    
    try:
        metrics = llm_service.get_analysis_metrics()
        
        return {
            "status": "success",
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis metrics: {str(e)}"
        ) 