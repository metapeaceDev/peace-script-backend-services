"""Centralised logging helpers with structured JSON output."""

from __future__ import annotations

import logging
import os
from logging.config import dictConfig

from pythonjsonlogger import jsonlogger


def _log_level() -> str:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    valid = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
    return level if level in valid else "INFO"


class PeaceJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter enforcing consistent field names for downstream collectors."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "fmt",
            "%(asctime)s %(levelname)s %(name)s %(message)s %(module)s %(process)d",
        )
        kwargs.setdefault(
            "rename_fields",
            {
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        )
        kwargs.setdefault("json_ensure_ascii", False)
        super().__init__(*args, **kwargs)


def _build_logging_config() -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": PeaceJsonFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": _log_level(),
                "propagate": False,
            },
        },
    }


def get_logger(name: str) -> logging.LoggerAdapter[logging.Logger]:
    dictConfig(_build_logging_config())
    base_logger = logging.getLogger(name)
    return logging.LoggerAdapter(base_logger, {"app": "peace-script-backend"})
