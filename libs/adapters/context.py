from contextvars import ContextVar
from typing import Optional, Any

# Context variables for dependency injection
crm_adapter_ctx: ContextVar[Optional[Any]] = ContextVar("crm_adapter", default=None)
erp_adapter_ctx: ContextVar[Optional[Any]] = ContextVar("erp_adapter", default=None)
whatsapp_adapter_ctx: ContextVar[Optional[Any]] = ContextVar("whatsapp_adapter", default=None)
email_adapter_ctx: ContextVar[Optional[Any]] = ContextVar("email_adapter", default=None)
