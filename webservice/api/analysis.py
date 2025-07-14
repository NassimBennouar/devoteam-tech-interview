from fastapi import APIRouter, HTTPException
from webservice.services.llm_analysis import LLMAnalysisService
from webservice.services.anomaly_detection import AnomalyDetectionService
from webservice.models.analysis import AnalysisResult
from webservice.api.metrics import get_latest_metrics
import logging
import os

router = APIRouter()
llm_service = LLMAnalysisService()
anomaly_service = AnomalyDetectionService()
logger = logging.getLogger(__name__)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


@router.get("/analysis", response_model=AnalysisResult)
async def get_analysis():
    if DEBUG:
        logger.debug("Analysis endpoint called")
    
    latest_metrics = get_latest_metrics()
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