"""Structured logging entry point.

Provides :class:`StructuredLogger` — a thin wrapper over the standard library
:class:`logging.Logger` that:

* carries bound context fields (turn, day, player, strategy, component,
  action, correlation id, decision id, execution time) so every record is a
  self-describing structured event;
* integrates with the canonical :class:`~agent.logging.formatter.JSONFormatter`;
* exposes intent-specific helpers (:meth:`decision`, :meth:`performance`).

The package is configured once via :func:`configure_logging` from a
:class:`~agent.config.settings.Settings` instance.
"""
from __future__ import annotations

import logging
import threading
from typing import Any

from agent.config.settings import Settings

from .handlers import InMemoryHandler, get_console_handler, get_file_handler, get_in_memory_handler

_DEFAULT_LEVEL = logging.INFO
_LOCK = threading.Lock()
_CONFIGURED: set[str] = set()
_GLOBAL_LEVEL: list[int] = [logging.NOTSET]
_REPLAY_HANDLER: list[InMemoryHandler | None] = [None]

#: Canonical structured context fields carried on every record.
_CONTEXT_FIELDS = (
    "turn",
    "day",
    "hour",
    "player",
    "strategy",
    "component",
    "action",
    "correlation_id",
    "decision_id",
    "execution_time_ms",
)


class StructuredLogger:
    """Logger that binds structured context to every emitted record."""

    def __init__(
        self,
        name: str,
        *,
        level: int | str = _DEFAULT_LEVEL,
        structured: bool = True,
        propagate: bool = True,
    ) -> None:
        self._logger = logging.getLogger(name)
        self._context: dict[str, Any] = {}
        self._structured = structured
        self._propagate = propagate
        self.setLevel(level)

    # -- configuration ----------------------------------------------------
    @property
    def name(self) -> str:
        return self._logger.name

    def setLevel(self, level: int | str) -> None:  # noqa: N802 (stdlib parity)
        self._logger.setLevel(level)

    def isEnabledFor(self, level: int) -> bool:  # noqa: N802
        return self._logger.isEnabledFor(level)

    def get_effective_level(self) -> int:
        return self._logger.getEffectiveLevel()

    # -- context binding --------------------------------------------------
    def bind(self, **context: Any) -> StructuredLogger:
        """Return a new logger with the given context fields merged in."""
        child = StructuredLogger(
            self._logger.name,
            level=self._logger.level,
            structured=self._structured,
            propagate=self._propagate,
        )
        child._context = {**self._context, **{k: v for k, v in context.items() if v is not None}}
        child._logger = self._logger
        return child

    def with_fields(self, **context: Any) -> StructuredLogger:
        return self.bind(**context)

    # -- emission ---------------------------------------------------------
    def _emit(
        self,
        level: int,
        msg: str,
        *args: Any,
        exc_info: Any = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        **extra: Any,
    ) -> None:
        if not self._logger.isEnabledFor(level):
            return
        record_extra = {
            k: v for k, v in {**self._context, **extra}.items() if v is not None
        }
        self._logger._log(
            level, msg, args, exc_info=exc_info, stack_info=stack_info,
            stacklevel=stacklevel, extra=record_extra or None,
        )

    def debug(self, msg: str, *args: Any, **extra: Any) -> None:
        self._emit(logging.DEBUG, msg, *args, **extra)

    def info(self, msg: str, *args: Any, **extra: Any) -> None:
        self._emit(logging.INFO, msg, *args, **extra)

    def warning(self, msg: str, *args: Any, **extra: Any) -> None:
        self._emit(logging.WARNING, msg, *args, **extra)

    warn = warning

    def error(self, msg: str, *args: Any, **extra: Any) -> None:
        self._emit(logging.ERROR, msg, *args, **extra)

    def critical(self, msg: str, *args: Any, **extra: Any) -> None:
        self._emit(logging.CRITICAL, msg, *args, **extra)

    fatal = critical

    def exception(self, msg: str, *args: Any, **extra: Any) -> None:
        self._emit(logging.ERROR, msg, *args, exc_info=True, **extra)

    # -- intent-specific helpers -----------------------------------------
    def decision(
        self,
        msg: str,
        *,
        step: int,
        day: int,
        decision_id: str,
        component: str = "",
        action: str = "",
        **extra: Any,
    ) -> None:
        """Emit a structured *decision* log entry."""
        self.info(
            msg,
            turn=step,
            day=day,
            component=component or self._logger.name,
            action=action,
            decision_id=decision_id,
            **extra,
        )

    def performance(
        self,
        component: str,
        execution_time_ms: float,
        **extra: Any,
    ) -> None:
        """Emit a structured *performance* log entry."""
        self.info(
            "performance metric",
            component=component,
            execution_time_ms=round(float(execution_time_ms), 3),
            **extra,
        )

    # -- delegation -------------------------------------------------------
    def addHandler(self, handler: logging.Handler) -> None:  # noqa: N802
        self._logger.addHandler(handler)

    def removeHandler(self, handler: logging.Handler) -> None:  # noqa: N802
        self._logger.removeHandler(handler)

    @property
    def handlers(self) -> list[logging.Handler]:
        return self._logger.handlers

    def set_propagate(self, propagate: bool) -> None:
        self._logger.propagate = propagate


def _ensure_null_handler(logger: logging.Logger) -> None:
    """Library best practice: ensure a logger has at least a NullHandler."""
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())


def get_logger(
    name: str,
    *,
    level: int | str = _DEFAULT_LEVEL,
    structured: bool = True,
    propagate: bool = True,
    **context: Any,
) -> StructuredLogger:
    """Return a :class:`StructuredLogger` for ``name``.

    Unlike the standard library, this does **not** attach a console handler to
    every named logger (which causes duplicate output under propagation).
    Call :func:`configure_logging` once during start-up to wire up handlers.
    """
    logger = StructuredLogger(name, level=level, structured=structured, propagate=propagate)
    _ensure_null_handler(logger._logger)
    base = logging.getLogger("agent")
    _ensure_null_handler(base)
    logger.bind(**context)
    return logger


def get_replay_handler() -> InMemoryHandler | None:
    return _REPLAY_HANDLER[0]


def configure_logging(
    settings: Settings | None = None,
    *,
    logger_name: str = "agent",
    force: bool = False,
) -> None:
    """Configure structured logging from ``settings``.

    Attaches console, file, and (optionally) in-memory handlers to the
    ``agent`` logger hierarchy.  Safe to call multiple times; pass
    ``force=True`` to replace existing handlers.
    """
    settings = settings or _default_settings()
    with _LOCK:
        root = logging.getLogger(logger_name)
        if _CONFIGURED and logger_name in _CONFIGURED and not force:
            return

        log_cfg = settings.logging or {}
        structured = bool(log_cfg.get("structured", True))
        level = _parse_level(settings.log_level or log_cfg.get("level", "INFO"))

        root.setLevel(level)
        if force:
            for h in list(root.handlers):
                root.removeHandler(h)
        else:
            # Replace any legacy handlers installed by get_logger().
            for h in list(root.handlers):
                if not isinstance(h, logging.NullHandler):
                    root.removeHandler(h)

        console = get_console_handler(level, structured=structured)
        root.addHandler(console)

        log_file = log_cfg.get("file")
        if log_file:
            root.addHandler(
                get_file_handler(log_file, level, structured=structured)
            )

        # In-memory capture for replay analysis when tracing/replay is on.
        if settings.is_feature_enabled("ENABLE_TRACE") or settings.is_feature_enabled(
            "ENABLE_DECISION_REPLAY"
        ):
            replay = get_in_memory_handler(level, structured=structured, max_records=5000)
            root.addHandler(replay)
            _REPLAY_HANDLER[0] = replay

        root.propagate = False
        _CONFIGURED.add(logger_name)
        _GLOBAL_LEVEL[0] = level


def _default_settings() -> Settings:
    try:
        from agent.config import get_config

        return get_config()
    except Exception:
        return Settings()


def _parse_level(level: str | int) -> int:
    if isinstance(level, int):
        return level
    mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return mapping.get(str(level).upper(), logging.INFO)


def set_global_level(level: str | int) -> None:
    """Adjust the verbosity of the configured ``agent`` logger at runtime."""
    parsed = _parse_level(level)
    _GLOBAL_LEVEL[0] = parsed
    logging.getLogger("agent").setLevel(parsed)
