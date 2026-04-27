from typing import Any, Dict, Optional
from .base import BaseERPAdapter

class SAPERPAdapter(BaseERPAdapter):
    async def get_account_aging(self, client_id: str) -> Dict[str, Any]:
        # Mock data
        return {
            "client_id": client_id,
            "total_debt": 5000.0,
            "overdue_30_days": 1200.0,
            "overdue_60_days": 500.0,
            "risk_level": "medium"
        }

    async def apply_operational_change(self, client_id: str, change_type: str, details: Dict[str, Any]) -> bool:
        print(f"[ERP] SAP applied {change_type} for {client_id}: {details}")
        return True
