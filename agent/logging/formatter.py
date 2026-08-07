"""Structured log formatters.

Two formatters are provided:

* :class:`JSONFormatter` — emits every log record as a single-line JSON
  object containing the canonical operational fields (timestamp, turn, day,
  player id, strategy, component, action, execution time, severity,
  correlation id, decision id, message).
* :class:`StandardFormatter` — human-readable plain-text output for
  interactive / console use.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

#: Fields that stdlib's :class:`logging.LogRecord` reserves; values here must
#: not be passed via ``extra``.
RESERVED = frozenset(
    {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "funcName", "lineno",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "process", "processName", "taskName", "message", "asctime",
    }
)

#: Canonical ordered set of structured context fields the formatter emits.
STRUCTURED_FIELDS = (
    "timestamp",
    "turn",
    "day",
    "hour",
    "player",
    "strategy",
    "component",
    "action",
    "execution_time_ms",
    "severity",
    "correlation_id",
    "decision_id",
)


class JSONFormatter(logging.Formatter):
    """Render :class:`logging.LogRecord` objects as structured JSON."""

    def __init__(self, *, include_source: bool = True) -> None:
        super().__init__()
        self._include_source = include_source

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {}
        for field in STRUCTURED_FIELDS:
            payload[field] = getattr(record, field, None)

        payload["timestamp"] = datetime.fromtimestamp(
            record.created, tz=UTC
        ).isoformat(timespec="milliseconds")
        if payload["component"] is None:
            payload["component"] = record.name
        payload["severity"] = record.levelname
        payload["message"] = record.getMessage()

        if self._include_source:
            payload["source"] = (
                f"{record.module}:{record.funcName}:{record.lineno}"
            )

        # Carry any additional (non-reserved) structured extras.
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in RESERVED and k not in STRUCTURED_FIELDS
            and k != "message"
        }
        if extras:
            payload["extra"] = extras

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)

        return json.dumps(payload, default=str, sort_keys=False)


class StandardFormatter(logging.Formatter):
    """Human-readable formatter that prefixes structured context fields."""

    def format(self, record: logging.LogRecord) -> str:
        ctx_parts = []
        for field in STRUCTURED_FIELDS:
            value = getattr(record, field, None)
            if value is not None and field not in ("timestamp", "severity"):
                ctx_parts.append(f"{field}={value}")
        prefix = f"[{' '.join(ctx_parts)}] " if ctx_parts else ""
        base = super().format(record)
        return f"{prefix}{base}"
