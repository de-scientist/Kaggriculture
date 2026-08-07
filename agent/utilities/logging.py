"""Backward-compatible logging helper.

Delegates to the canonical :mod:`agent.logging` structured-logging package so
that existing call-sites using ``from agent.utilities.logging import get_logger``
keep working with structured, context-aware logging.
"""

from __future__ import annotations

import logging
from typing import Any

from agent.logging import StructuredLogger, configure_logging
from agent.logging import get_logger as _get_logger

__all__ = ["StructuredLogger", "configure_logging", "get_logger", "get_stdlib_logger"]


def get_logger(name: str, **context: Any) -> StructuredLogger:
    """Return a :class:`StructuredLogger` bound to ``name``.

    Accepts optional structured context fields (turn, day, player, ...).
    """
    return _get_logger(name, **context)


def get_stdlib_logger(name: str) -> logging.Logger:
    """Return the underlying standard-library logger for ``name``."""
    return logging.getLogger(name)
