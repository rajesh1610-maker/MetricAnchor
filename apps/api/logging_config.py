"""
Structured logging configuration.

Produces JSON lines to stdout in production (LOG_FORMAT=json)
and coloured human-readable output in development (default).

Usage:
    from logging_config import configure_logging
    configure_logging()   # call once at startup

Every log record emitted after this call includes:
  - timestamp (ISO-8601)
  - level
  - logger name
  - message
  - any extra keyword args passed to the logger
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Literal

from config import get_settings


class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: dict = {
            "ts": self.formatTime(record, datefmt=None),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Merge any extra fields attached via logger.info("…", extra={…})
        for key, val in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            }:
                try:
                    json.dumps(val)
                    payload[key] = val
                except (TypeError, ValueError):
                    payload[key] = str(val)
        return json.dumps(payload)


class _HumanFormatter(logging.Formatter):
    _COLOURS = {
        "DEBUG": "\033[37m",
        "INFO": "\033[36m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[1;31m",
    }
    _RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        colour = self._COLOURS.get(record.levelname, "")
        ts = self.formatTime(record, datefmt="%H:%M:%S")
        prefix = f"{colour}{record.levelname:<8}{self._RESET}"
        return f"{ts} {prefix} [{record.name}] {record.getMessage()}"


def configure_logging(
    level: str | None = None,
    fmt: Literal["json", "human"] | None = None,
) -> None:
    """
    Set up root logger and silence noisy third-party libraries.

    Args:
        level: override LOG_LEVEL env var (default INFO).
        fmt:   override LOG_FORMAT env var ("json" or "human").
    """
    import os

    effective_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    effective_fmt = fmt or os.getenv("LOG_FORMAT", "human")

    formatter: logging.Formatter
    if effective_fmt == "json":
        formatter = _JsonFormatter()
    else:
        formatter = _HumanFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(effective_level)
    # Remove default handlers added by uvicorn/fastapi
    root.handlers.clear()
    root.addHandler(handler)

    # Reduce noise from chatty libraries
    for noisy in ("sqlalchemy.engine", "sqlalchemy.pool", "httpx", "httpcore", "uvicorn.access"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("metricanchor").setLevel(effective_level)
