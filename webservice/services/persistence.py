from typing import Dict, Any, List, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from webservice.models.sql import User, Infrastructure, Metrics
from webservice.services.validation import ValidationService

logger = logging.getLogger(__name__)


class PersistenceService:
    def __init__(self):
        self.validation_service = ValidationService()

    async def store_metrics(self, session: AsyncSession, metrics_data: Dict[str, Any]) -> bool:
        try:
            user = await self._get_user(session, "jean")
            infra = await self._get_infrastructure(session, "default", user.id)
            
            metrics = Metrics(
                infra_id=infra.id,
                user_id=user.id,
                timestamp=metrics_data["timestamp"],
                cpu_usage=metrics_data["cpu_usage"],
                memory_usage=metrics_data["memory_usage"],
                latency_ms=metrics_data["latency_ms"],
                disk_usage=metrics_data["disk_usage"],
                network_in_kbps=metrics_data["network_in_kbps"],
                network_out_kbps=metrics_data["network_out_kbps"],
                io_wait=metrics_data["io_wait"],
                thread_count=metrics_data["thread_count"],
                active_connections=metrics_data["active_connections"],
                error_rate=metrics_data["error_rate"],
                uptime_seconds=metrics_data["uptime_seconds"],
                temperature_celsius=metrics_data["temperature_celsius"],
                power_consumption_watts=metrics_data["power_consumption_watts"],
                service_status_database=metrics_data["service_status"]["database"],
                service_status_api_gateway=metrics_data["service_status"]["api_gateway"],
                service_status_cache=metrics_data["service_status"]["cache"]
            )
            
            session.add(metrics)
            await session.commit()
            await session.refresh(metrics)
            
            logger.info(f"Metrics stored successfully with ID: {metrics.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing metrics: {str(e)}")
            await session.rollback()
            return False

    async def store_metrics_batch(self, session: AsyncSession, metrics_list: List[Dict[str, Any]]) -> Dict[str, int]:
        stored_count = 0
        failed_count = 0
        
        for i, metrics_data in enumerate(metrics_list):
            try:
                validation_result = self.validation_service.validate_metrics(metrics_data)
                
                if not validation_result.is_valid:
                    logger.warning(f"Metrics at index {i} failed validation: {len(validation_result.errors)} errors")
                    for error in validation_result.errors:
                        logger.debug(f"  - {error.field}: {error.message}")
                    failed_count += 1
                    continue
                
                success = await self.store_metrics(session, validation_result.data)
                if success:
                    stored_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing metrics at index {i}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Batch processing completed: {stored_count} stored, {failed_count} failed")
        return {"stored": stored_count, "failed": failed_count}

    async def _get_user(self, session: AsyncSession, username: str) -> User:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalar_one()
        if not user:
            raise ValueError(f"User '{username}' not found")
        return user

    async def _get_infrastructure(self, session: AsyncSession, name: str, user_id: int) -> Infrastructure:
        result = await session.execute(
            select(Infrastructure).where(
                Infrastructure.name == name,
                Infrastructure.user_id == user_id
            )
        )
        infra = result.scalar_one()
        if not infra:
            raise ValueError(f"Infrastructure '{name}' not found for user {user_id}")
        return infra 