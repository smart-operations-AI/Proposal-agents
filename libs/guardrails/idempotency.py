import hashlib
from datetime import datetime, timedelta
from libs.contracts.models import InternalSignal
from libs.persistence.database import get_async_engine, SignalRecord
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

class IdempotencyManager:
    """
    Manages signal idempotency using asynchronous PostgreSQL.
    Prevents duplicate actions for the same client and signal type within a specific window.
    """
    def __init__(self):
        self.engine = get_async_engine()
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    def generate_signal_hash(self, signal: InternalSignal) -> str:
        # Create a stable hash based on tenant, client, and signal type
        data = f"{signal.tenant_id}:{signal.client_id}:{signal.signal_type}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def is_duplicate(self, signal: InternalSignal, window_days: int = 7) -> bool:
        """
        Checks if a signal has already been executed recently for this client.
        """
        async with self.async_session() as session:
            cutoff_date = datetime.now() - timedelta(days=window_days)
            
            # Use select(SignalRecord) for async SQLAlchemy
            stmt = select(SignalRecord).where(
                SignalRecord.tenant_id == signal.tenant_id,
                SignalRecord.client_id == signal.client_id,
                SignalRecord.signal_type == signal.signal_type.value,
                SignalRecord.status == "EXECUTED",
                SignalRecord.expires_at > datetime.now()
            )
            
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if existing:
                print(f"[Idempotency] Signal {signal.signal_type} for {signal.client_id} already executed recently.")
                return True
            
        return False
