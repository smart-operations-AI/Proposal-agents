from typing import Dict, Any, Optional
from libs.contracts.models import InternalSignal, RevenueCommand

class PolicyEngine:
    def __init__(self, tenant_config: Dict[str, Any]):
        self.config = tenant_config

    async def validate_command(self, command: RevenueCommand, signal: InternalSignal) -> (bool, Optional[str]):
        """
        Validate a command against tenant-specific rules.
        """
        # 1. Margin Check
        min_margin = self.config.get("min_margin_pct", 10.0)
        current_margin = signal.metadata.get("current_margin", 20.0)
        
        if current_margin < min_margin:
            return False, f"Margin {current_margin}% is below minimum required {min_margin}%"

        # 2. Discount Cap
        max_discount = self.config.get("max_discount_pct", 15.0)
        proposed_discount = command.approved_params.get("max_discount", 0.0)
        
        if proposed_discount > max_discount:
            return False, f"Proposed discount {proposed_discount}% exceeds cap {max_discount}%"

        # 3. Frequency Cap (To be integrated with DB)
        # if await self._check_frequency(signal.client_id): ...

        return True, None

    async def is_strategic_account(self, client_id: str) -> bool:
        # Mock logic or CRM lookup
        return client_id.startswith("STRAT_")
