from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import os
from contextlib import asynccontextmanager

from api.health import router as health_router
from api.metrics import router as metrics_router
from api.anomalies import router as anomalies_router
from api.analysis import router as analysis_router

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Infrastructure Monitoring API starting up...")
    if DEBUG:
        logger.debug("Debug mode enabled")
    yield
    logger.info("Infrastructure Monitoring API shutting down...")

app = FastAPI(
    title="Infrastructure Monitoring API",
    description="API for infrastructure monitoring and optimization",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(metrics_router, prefix="/api", tags=["metrics"])
app.include_router(anomalies_router, prefix="/api", tags=["anomalies"])
app.include_router(analysis_router, prefix="/api", tags=["analysis"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 