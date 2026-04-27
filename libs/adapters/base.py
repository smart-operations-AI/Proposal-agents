from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from libs.contracts.models import ExecutionLog

class BaseCRMAdapter(ABC):
    @abstractmethod
    async def create_task(self, client_id: str, subject: str, description: str) -> str:
        """Create a task in the CRM and return the task ID."""
        pass

    @abstractmethod
    async def update_client_status(self, client_id: str, status: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update client status in CRM."""
        pass

class BaseERPAdapter(ABC):
    @abstractmethod
    async def get_account_aging(self, client_id: str) -> Dict[str, Any]:
        """Get financial aging data for a client."""
        pass

    @abstractmethod
    async def apply_operational_change(self, client_id: str, change_type: str, details: Dict[str, Any]) -> bool:
        """Apply a change in the ERP (e.g., credit hold)."""
        pass

class BaseMessagingAdapter(ABC):
    @abstractmethod
    async def send_message(self, recipient_id: str, content: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message and return the provider's response."""
        pass
