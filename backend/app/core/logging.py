"""
Structured logging configuration.
Supports both JSON and text formats for production and development.
"""
import logging
import sys
from typing import Any

import structlog
from structlog.processors import JSONRenderer, TimeStamper
from structlog.stdlib import add_log_level, add_logger_name

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""

    # Determine processors based on format
    processors = [
        structlog.stdlib.filter_by_level,
        add_log_level,
        add_logger_name,
        TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.LOG_FORMAT == "json":
        processors.append(JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )


def get_logger(name: str = __name__) -> Any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
