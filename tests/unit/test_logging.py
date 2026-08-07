"""Tests for the structured logging layer."""
from __future__ import annotations

import json
import logging

import pytest

from agent.config import Settings, reset_config
from agent.logging import (
    JSONFormatter,
    StandardFormatter,
    StructuredLogger,
    configure_logging,
    get_logger,
    get_replay_handler,
)
from agent.logging.handlers import InMemoryHandler, get_in_memory_handler


@pytest.fixture
def isolated_logger():
    """Provide a structured logger writing to a dedicated in-memory handler."""
    name = "test.isolated"
    logger = get_logger(name, propagate=False)
    handler = get_in_memory_handler(structured=True)
    logger.addHandler(handler)
    yield logger, handler
    logger.removeHandler(handler)


def test_get_logger_returns_structured_logger() -> None:
    logger = get_logger("test.structured")
    assert isinstance(logger, StructuredLogger)
    assert logger.name == "test.structured"


def test_bind_merges_context() -> None:
    logger = get_logger("test.bind")
    child = logger.bind(turn=10, day=3, player=0)
    assert child.name == logger.name
    assert child._context["turn"] == 10
    assert child._context["day"] == 3
    # parent not mutated
    assert logger._context == {}


def test_emits_json_with_bound_fields(isolated_logger) -> None:
    logger, handler = isolated_logger
    child = logger.bind(turn=7, day=2, player=1, strategy="baseline",
                       correlation_id="c-1234", decision_id="d-7",
                       component="Test", action="decide")
    child.info("hello %s", "world")
    assert len(handler.records) == 1
    formatted = handler.format(handler.records[0])
    payload = json.loads(formatted)
    assert payload["message"] == "hello world"
    assert payload["severity"] == "INFO"
    assert payload["turn"] == 7
    assert payload["day"] == 2
    assert payload["player"] == 1
    assert payload["strategy"] == "baseline"
    assert payload["correlation_id"] == "c-1234"
    assert payload["component"] == "Test"


def test_json_formatter_skips_none_fields(isolated_logger) -> None:
    logger, handler = isolated_logger
    logger.info("simple")
    formatted = json.loads(handler.formatter().format(handler.records[0]))
    assert "turn" in formatted
    assert formatted["turn"] is None


def test_standard_formatter_prefixes_context() -> None:
    formatter = StandardFormatter()
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "msg", (), None)
    record.turn = 5
    record.day = 1
    record.component = "Comp"
    line = formatter.format(record)
    assert "turn=5" in line
    assert "day=1" in line
    assert "component=Comp" in line
    assert "msg" in line


def test_configure_logging_from_settings() -> None:
    settings = Settings(logging={"level": "DEBUG", "structured": True})
    configure_logging(settings, logger_name="test.configure", force=True)
    root = logging.getLogger("test.configure")
    assert root.level == logging.DEBUG
    assert root.propagate is False
    # at least a console handler present
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)


def test_configure_logging_attaches_in_memory_when_trace_enabled() -> None:
    settings = Settings(features={"ENABLE_TRACE": True})
    configure_logging(settings, logger_name="test.replay_handler", force=True)
    assert get_replay_handler() is not None
    assert isinstance(get_replay_handler(), InMemoryHandler)


def test_configure_logging_idempotent_without_force() -> None:
    settings = Settings(logging={"level": "INFO"})
    configure_logging(settings, logger_name="test.idempotent")
    count_after_first = len(logging.getLogger("test.idempotent").handlers)
    configure_logging(settings, logger_name="test.idempotent")
    count_after_second = len(logging.getLogger("test.idempotent").handlers)
    assert count_after_first == count_after_second


def test_performance_helper_emits_metric(isolated_logger) -> None:
    logger, handler = isolated_logger
    logger.performance("DecisionEngine", 12.5, turn=1, day=0, player=0)
    formatted = json.loads(handler.formatter().format(handler.records[0]))
    assert formatted["component"] == "DecisionEngine"
    assert formatted["execution_time_ms"] == 12.5


def test_exception_logs_with_traceback(isolated_logger) -> None:
    logger, handler = isolated_logger
    try:
        raise ValueError("inner")
    except ValueError:
        logger.exception("caught it")
    record = handler.records[-1]
    formatted = json.loads(handler.formatter().format(record))
    assert formatted["severity"] == "ERROR"
    assert "Traceback" in formatted["exception"]
    assert "ValueError" in formatted["exception"]


def test_in_memory_handler_captures_records() -> None:
    handler = get_in_memory_handler(level=logging.DEBUG, structured=False)
    logger = logging.getLogger("test.inmemory")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.info("captured")
    assert len(handler.records) == 1
    assert handler.records[0].getMessage() == "captured"
    as_dicts = handler.as_dicts()
    assert as_dicts[0]["message"] == "captured"
