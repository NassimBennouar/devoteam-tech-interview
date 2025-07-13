from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from webservice.api.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Infrastructure Monitoring API starting up...")
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 