from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import datetime
import os

Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True)
    name = Column(String)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SignalRecord(Base):
    __tablename__ = "signals"
    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"))
    client_id = Column(String)
    signal_type = Column(String)
    priority_score = Column(Integer)
    estimated_revenue_impact = Column(Float)
    segment = Column(String)
    expires_at = Column(DateTime)
    requires_human_review = Column(Boolean, default=False)
    status = Column(String, default="PENDING")
    metadata_json = Column(JSON)

class ExecutionRecord(Base):
    __tablename__ = "executions"
    id = Column(String, primary_key=True)
    signal_id = Column(String, ForeignKey("signals.id"))
    tenant_id = Column(String)
    action_type = Column(String)
    channel = Column(String)
    scheduled_at = Column(DateTime)
    executed_at = Column(DateTime)
    status = Column(String)
    retry_count = Column(Integer, default=0)

class OutcomeRecord(Base):
    __tablename__ = "outcomes"
    id = Column(String, primary_key=True)
    execution_id = Column(String, ForeignKey("executions.id"))
    signal_id = Column(String)
    tenant_id = Column(String)
    outcome_status = Column(String)
    revenue_generated = Column(Float, default=0.0)
    revenue_protected = Column(Float, default=0.0)
    attribution_confidence = Column(Float)
    outcome_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    time_to_outcome_minutes = Column(Integer)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String)
    entity_id = Column(String)
    entity_type = Column(String)
    action = Column(String)
    actor = Column(String)
    previous_state = Column(JSON)
    new_state = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Utility to get engine (Sync)
def get_engine(connection_string=None):
    if connection_string is None:
        connection_string = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/revenue_db")
    return create_engine(connection_string)

# Utility to get async engine
def get_async_engine(connection_string=None):
    if connection_string is None:
        # Default to asyncpg driver if not specified
        url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/revenue_db")
        if "asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        connection_string = url
    return create_async_engine(connection_string)

def init_db(engine):
    Base.metadata.create_all(engine)
