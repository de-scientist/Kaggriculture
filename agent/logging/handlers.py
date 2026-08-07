"""Logging handlers for the Kaggriculture AI platform."""
from __future__ import annotations

import logging
import sys
from collections import deque
from pathlib import Path
from typing import Any

from agent.logging.formatter import JSONFormatter


class InMemoryHandler(logging.Handler):
    """Capture log records in memory for testing, profiling and replay.

    Records are stored in a bounded :class:`collections.deque` so that long
    running sessions cannot exhaust memory.  Iteration yields the most recent
    records first.
    """

    def __init__(self, level: int = logging.NOTSET, max_records: int = 5000) -> None:
        super().__init__(level)
        self._records: deque[logging.LogRecord] = deque(maxlen=max_records)
        self._json: bool = False

    @property
    def records(self) -> list[logging.LogRecord]:
        return list(self._records)

    def as_dicts(self) -> list[dict[str, Any]]:
        return [self._record_to_dict(r) for r in self._records]

    def _record_to_dict(self, record: logging.LogRecord) -> dict[str, Any]:
        if self._json:
            message = JSONFormatter().format(record)
        else:
            message = record.getMessage()
        return {"level": record.levelname, "message": message}

    def set_structured(self, structured: bool) -> None:
        self._json = structured
        if structured:
            self.setFormatter(JSONFormatter())
        else:
            self.setFormatter(logging.Formatter("%(message)s"))

    def clear(self) -> None:
        self._records.clear()

    def emit(self, record: logging.LogRecord) -> None:
        self._records.append(record)
        if self.formatter is None:
            self.format(record)


def get_console_handler(
    level: int = logging.INFO,
    *,
    structured: bool = False,
    stream: Any = None,
) -> logging.Handler:
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setLevel(level)
    if structured:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    return handler


def get_file_handler(
    path: str | Path,
    level: int = logging.DEBUG,
    *,
    structured: bool = False,
) -> logging.Handler:
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Cannot create log directory; fall back to stderr-only.
        return get_console_handler(level, structured=structured, stream=sys.stderr)
    handler = logging.FileHandler(p, encoding="utf-8")
    handler.setLevel(level)
    if structured:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    return handler


def get_in_memory_handler(
    level: int = logging.DEBUG,
    *,
    structured: bool = False,
    max_records: int = 5000,
) -> InMemoryHandler:
    handler = InMemoryHandler(level=level, max_records=max_records)
    handler.set_structured(structured)
    return handler
