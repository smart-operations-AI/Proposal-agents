from typing import Dict, Any, Optional
from libs.contracts.models import InternalSignal, RevenueCommand

class PolicyEngine:
    def __init__(self, tenant_config: Dict[str, Any]):
        self.config = tenant_config

    async def validate_command(self, command: RevenueCommand, signal: InternalSignal) -> (bool, Optional[str]):
        """
        Validate a command using ONLY tenant-specific configuration.
        """
        # 1. Margin Check
        min_margin = self.config.get("min_margin_pct")
        if min_margin is None:
            return False, "Configuration error: min_margin_pct not defined for tenant"
            
        current_margin = signal.metadata.get("current_margin")
        if current_margin is None:
            return False, "Data error: current_margin missing from signal metadata"
        
        if current_margin < min_margin:
            return False, f"Margin {current_margin}% is below minimum required {min_margin}%"

        # 2. Discount Cap
        max_discount = self.config.get("max_discount_pct")
        if max_discount is None:
            return False, "Configuration error: max_discount_pct not defined for tenant"
            
        proposed_discount = command.approved_params.get("max_discount", 0.0)
        if proposed_discount > max_discount:
            return False, f"Proposed discount {proposed_discount}% exceeds cap {max_discount}%"

        return True, None

    async def is_strategic_account(self, client_id: str) -> bool:
        # Check against a provided list in the config
        strategic_list = self.config.get("strategic_accounts", [])
        return client_id in strategic_list or client_id.startswith("STRAT_")
