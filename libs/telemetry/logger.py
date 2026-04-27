import structlog
import logging
import sys
from typing import Any, Dict

def setup_logging():
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str):
    return structlog.get_logger(name)

class AgentLogger:
    def __init__(self, agent_name: str, tenant_id: str, trace_id: str):
        self.logger = get_logger(agent_name).bind(
            tenant_id=tenant_id,
            trace_id=trace_id
        )

    def info(self, event: str, **kwargs):
        self.logger.info(event, **kwargs)

    def error(self, event: str, error: Exception, **kwargs):
        self.logger.error(event, error=str(error), **kwargs)
