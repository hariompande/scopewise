"""
Logging configuration for the application
"""

import json
import logging
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
            
        return json.dumps(log_data)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger with JSON formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def info(message: str, **kwargs: Any) -> None:
    """Log an info message."""
    logger = logging.getLogger(__name__)
    extra_data = kwargs if kwargs else None
    if extra_data:
        logger.info(message, extra={"extra_data": extra_data})
    else:
        logger.info(message)


def error(message: str, **kwargs: Any) -> None:
    """Log an error message."""
    logger = logging.getLogger(__name__)
    extra_data = kwargs if kwargs else None
    if extra_data:
        logger.error(message, extra={"extra_data": extra_data})
    else:
        logger.error(message)


def warning(message: str, **kwargs: Any) -> None:
    """Log a warning message."""
    logger = logging.getLogger(__name__)
    extra_data = kwargs if kwargs else None
    if extra_data:
        logger.warning(message, extra={"extra_data": extra_data})
    else:
        logger.warning(message)


def debug(message: str, **kwargs: Any) -> None:
    """Log a debug message."""
    logger = logging.getLogger(__name__)
    extra_data = kwargs if kwargs else None
    if extra_data:
        logger.debug(message, extra={"extra_data": extra_data})
    else:
        logger.debug(message)
