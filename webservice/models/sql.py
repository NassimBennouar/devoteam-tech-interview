from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from webservice.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    infrastructures = relationship("Infrastructure", back_populates="user")

class Infrastructure(Base):
    __tablename__ = "infrastructures"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metrics = relationship("Metrics", back_populates="infrastructure")
    user = relationship("User", back_populates="infrastructures")

class Metrics(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    infra_id = Column(Integer, ForeignKey("infrastructures.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(String, index=True, nullable=False)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    latency_ms = Column(Float)
    disk_usage = Column(Float)
    network_in_kbps = Column(Float)
    network_out_kbps = Column(Float)
    io_wait = Column(Float)
    thread_count = Column(Integer)
    active_connections = Column(Integer)
    error_rate = Column(Float)
    uptime_seconds = Column(Float)
    temperature_celsius = Column(Float)
    power_consumption_watts = Column(Float)
    service_status_database = Column(String)
    service_status_api_gateway = Column(String)
    service_status_cache = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    infrastructure = relationship("Infrastructure", back_populates="metrics") 