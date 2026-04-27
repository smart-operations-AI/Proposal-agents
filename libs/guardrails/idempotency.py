import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional
from libs.contracts.models import InternalSignal
from libs.persistence.database import get_engine, SignalRecord
from sqlalchemy.orm import sessionmaker

class IdempotencyManager:
    def __init__(self, db_url: str = "sqlite:///./revenue_agents.db"):
        self.engine = get_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def generate_signal_hash(self, signal: InternalSignal) -> str:
        # Create a stable hash based on tenant, client, and signal type
        data = f"{signal.tenant_id}:{signal.client_id}:{signal.signal_type}"
        return hashlib.sha256(data.encode()).hexdigest()

    async def is_duplicate(self, signal: InternalSignal, window_days: int = 7) -> bool:
        signal_hash = self.generate_signal_hash(signal)
        
        with self.Session() as session:
            # Check for existing signals of same type for same client within the window
            cutoff_date = datetime.now() - timedelta(days=window_days)
            existing = session.query(SignalRecord).filter(
                SignalRecord.tenant_id == signal.tenant_id,
                SignalRecord.client_id == signal.client_id,
                SignalRecord.signal_type == signal.signal_type,
                SignalRecord.status == "EXECUTED",
                SignalRecord.expires_at > datetime.now() # Still valid?
            ).first()
            
            if existing:
                print(f"[Idempotency] Signal {signal.signal_type} for {signal.client_id} already executed recently.")
                return True
            
        return False
