from fastapi import APIRouter
from webservice.models.metrics import ApiResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=ApiResponse)
async def health_check():
    logger.info("Health check requested")
    
    return ApiResponse(
        status="ok",
        message="Infrastructure Monitoring API is running",
        data={
            "timestamp": datetime.now().isoformat(),
            "version": "0.1.0"
        }
    ) 