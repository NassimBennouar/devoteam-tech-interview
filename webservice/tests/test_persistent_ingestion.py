import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from webservice.main import app
from webservice.db import engine, Base
from webservice.models.sql import User, Infrastructure
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sqlalchemy
import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        user = User(username="jean", password="jean")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        infra = Infrastructure(name="default", user_id=user.id)
        session.add(infra)
        await session.commit()
    yield

@pytest.fixture
def valid_metrics_data():
    return {
        "timestamp": "2023-10-01T12:00:00Z",
        "cpu_usage": 85,
        "memory_usage": 75,
        "latency_ms": 150,
        "disk_usage": 60,
        "network_in_kbps": 1000,
        "network_out_kbps": 800,
        "io_wait": 5,
        "thread_count": 50,
        "active_connections": 100,
        "error_rate": 0.02,
        "uptime_seconds": 3600,
        "temperature_celsius": 45,
        "power_consumption_watts": 300,
        "service_status": {
            "database": "online",
            "api_gateway": "online",
            "cache": "online"
        }
    }

@pytest.fixture
def invalid_metrics_data():
    return {
        "timestamp": "2023-10-01T12:00:00Z",
        "cpu_usage": "invalid",
        "memory_usage": 75,
        "latency_ms": 150,
        "disk_usage": 60,
        "network_in_kbps": 1000,
        "network_out_kbps": 800,
        "io_wait": 5,
        "thread_count": 50,
        "active_connections": 100,
        "error_rate": 0.02,
        "uptime_seconds": 3600,
        "temperature_celsius": 45,
        "power_consumption_watts": 300,
        "service_status": {
            "database": "online",
            "api_gateway": "online",
            "cache": "online"
        }
    }

import pytest_asyncio

@pytest.mark.asyncio
async def test_single_metrics_ingestion_success(valid_metrics_data):
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json=valid_metrics_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "processing_time" in data
        assert data["data"]["cpu_usage"] == 85

@pytest.mark.asyncio
async def test_single_metrics_ingestion_validation_error(invalid_metrics_data):
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json=invalid_metrics_data)
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"
        assert "errors" in data
        assert any(e["field"] == "cpu_usage" for e in data["errors"])

@pytest.mark.asyncio
async def test_batch_metrics_ingestion_success(valid_metrics_data):
    batch_data = [valid_metrics_data.copy() for _ in range(3)]
    batch_data[1]["timestamp"] = "2023-10-01T12:01:00Z"
    batch_data[2]["timestamp"] = "2023-10-01T12:02:00Z"
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json=batch_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "batch_result" in data
        assert data["batch_result"]["stored"] == 3
        assert data["batch_result"]["failed"] == 0

@pytest.mark.asyncio
async def test_batch_metrics_ingestion_partial_success(valid_metrics_data, invalid_metrics_data):
    batch_data = [valid_metrics_data, invalid_metrics_data, valid_metrics_data.copy()]
    batch_data[2]["timestamp"] = "2023-10-01T12:02:00Z"
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json=batch_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["batch_result"]["stored"] == 2
        assert data["batch_result"]["failed"] == 1

@pytest.mark.asyncio
async def test_batch_metrics_ingestion_all_invalid(invalid_metrics_data):
    batch_data = [invalid_metrics_data, invalid_metrics_data]
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json=batch_data)
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"
        assert data["batch_result"]["stored"] == 0
        assert data["batch_result"]["failed"] == 2

@pytest.mark.asyncio
async def test_invalid_data_format():
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json="invalid")
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"
        assert "must be a dictionary" in data["message"]

@pytest.mark.asyncio
async def test_metrics_persistence_in_database(valid_metrics_data):
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json=valid_metrics_data)
        assert response.status_code == 200
        async with AsyncSession(engine) as session:
            from webservice.models.sql import Metrics
            result = await session.execute(select(Metrics))
            metrics = result.scalars().all()
            assert len(metrics) == 1
            assert metrics[0].cpu_usage == 85
            assert metrics[0].memory_usage == 75
            assert metrics[0].service_status_database == "online"

@pytest.mark.asyncio
async def test_batch_persistence_in_database(valid_metrics_data):
    batch_data = [valid_metrics_data.copy() for _ in range(3)]
    batch_data[1]["timestamp"] = "2023-10-01T12:01:00Z"
    batch_data[2]["timestamp"] = "2023-10-01T12:02:00Z"
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app)) as client:
        response = await client.post("/api/ingest", json=batch_data)
        assert response.status_code == 200
        async with AsyncSession(engine) as session:
            from webservice.models.sql import Metrics
            result = await session.execute(select(Metrics))
            metrics = result.scalars().all()
            assert len(metrics) == 3
            timestamps = [m.timestamp for m in metrics]
            assert "2023-10-01T12:00:00Z" in timestamps
            assert "2023-10-01T12:01:00Z" in timestamps
            assert "2023-10-01T12:02:00Z" in timestamps 