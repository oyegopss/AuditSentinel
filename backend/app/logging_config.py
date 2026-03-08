"""
Structured logging for AuditSentinel backend (Python logging module).
JSON one-line records with event type and context.

Standard events:
  - task_submitted: Task received (description_len)
  - agent_decision: AI decision generation (task_id, risk, recommended_action, confidence)
  - risk_detection: Risk classification (source, risk, score; scenario if source=scenario)
  - approval: Human approval actions (status, scenario, user, risk, action_hash, tx_hash)
  - blockchain_transaction: On-chain log (action_hash, tx_hash, user, timestamp)
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Format log records as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "event": getattr(record, "event", None),
        }
        # Include any extra fields set on the record
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "taskName", "event",
            ) and value is not None:
                log_obj[key] = value
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj, default=str)


def setup_logging(
    level: str = "INFO",
    stream: Any = None,
) -> None:
    """Configure root logger with structured formatter and level."""
    if stream is None:
        stream = sys.stdout
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredFormatter())
    root = logging.getLogger("app")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)
    # Prevent propagation to root to avoid duplicate lines
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a logger under the app namespace for structured logs."""
    return logging.getLogger(f"app.{name}")
