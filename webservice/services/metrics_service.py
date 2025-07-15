from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from webservice.models.sql import Metrics
import logging

logger = logging.getLogger(__name__)


class MetricsService:
    async def get_latest_metrics(self, session: AsyncSession) -> Optional[Dict[str, Any]]:
        try:
            result = await session.execute(
                select(Metrics).order_by(desc(Metrics.timestamp)).limit(1)
            )
            metric = result.scalar_one_or_none()
            
            if metric:
                return {
                    "timestamp": metric.timestamp,
                    "cpu_usage": metric.cpu_usage,
                    "memory_usage": metric.memory_usage,
                    "latency_ms": metric.latency_ms,
                    "disk_usage": metric.disk_usage,
                    "network_in_kbps": metric.network_in_kbps,
                    "network_out_kbps": metric.network_out_kbps,
                    "io_wait": metric.io_wait,
                    "thread_count": metric.thread_count,
                    "active_connections": metric.active_connections,
                    "error_rate": metric.error_rate,
                    "uptime_seconds": metric.uptime_seconds,
                    "temperature_celsius": metric.temperature_celsius,
                    "power_consumption_watts": metric.power_consumption_watts,
                    "service_status": {
                        "database": metric.service_status_database,
                        "api_gateway": metric.service_status_api_gateway,
                        "cache": metric.service_status_cache
                    }
                }
            return None
        except Exception as e:
            logger.error(f"Error getting latest metrics from DB: {str(e)}")
            return None

    async def get_historical_metrics(self, session: AsyncSession, points: int = 50) -> List[Dict[str, Any]]:
        try:
            result = await session.execute(
                select(Metrics).order_by(desc(Metrics.timestamp)).limit(points)
            )
            metrics = result.scalars().all()
            
            metrics_list = []
            for metric in metrics:
                metrics_list.append({
                    "timestamp": metric.timestamp,
                    "cpu_usage": metric.cpu_usage,
                    "memory_usage": metric.memory_usage,
                    "latency_ms": metric.latency_ms,
                    "disk_usage": metric.disk_usage,
                    "network_in_kbps": metric.network_in_kbps,
                    "network_out_kbps": metric.network_out_kbps,
                    "io_wait": metric.io_wait,
                    "thread_count": metric.thread_count,
                    "active_connections": metric.active_connections,
                    "error_rate": metric.error_rate,
                    "uptime_seconds": metric.uptime_seconds,
                    "temperature_celsius": metric.temperature_celsius,
                    "power_consumption_watts": metric.power_consumption_watts,
                    "service_status": {
                        "database": metric.service_status_database,
                        "api_gateway": metric.service_status_api_gateway,
                        "cache": metric.service_status_cache
                    }
                })
            
            logger.info(f"Retrieved {len(metrics_list)} historical metrics")
            return metrics_list
            
        except Exception as e:
            logger.error(f"Error getting historical metrics from DB: {str(e)}")
            return [] 