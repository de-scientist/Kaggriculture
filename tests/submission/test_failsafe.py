"""Tests for the Stage 4 fail-safe wrapper and emergency fallback."""

from __future__ import annotations

import logging
from typing import Any

from agent.submission.failsafe import (
    EMERGENCY_ACTION,
    FailSafeAgent,
    legalize,
    wrap_module,
)


def _ok_agent(obs: dict[str, Any]) -> dict[str, Any]:
    return {"farmer": ["PASS"], "hands": [], "market": []}


def _boom_agent(obs: dict[str, Any]) -> dict[str, Any]:
    raise RuntimeError("kaboom")


def test_legalize_repairs_malformed() -> None:
    assert legalize(None) == EMERGENCY_ACTION
    assert legalize({"farmer": []})["farmer"] == ["PASS"]
    assert legalize({"farmer": ["WATER"], "hands": "x"})["hands"] == []
    assert legalize({"farmer": ["WATER"]})["market"] == []


def test_failsafe_returns_normal_action() -> None:
    wrapped = FailSafeAgent(_ok_agent)
    assert wrapped({}) == {"farmer": ["PASS"], "hands": [], "market": []}


def test_failsafe_catches_exception() -> None:
    captured: list[logging.LogRecord] = []

    class _Cap(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            captured.append(record)

    log = logging.getLogger("agent.submission.failsafe.test")
    log.addHandler(_Cap())
    try:
        wrapped = FailSafeAgent(_boom_agent, logger=log)
        out = wrapped({})
        assert out == EMERGENCY_ACTION
        assert any("emergency fallback" in r.getMessage() for r in captured)
    finally:
        log.removeHandler(_Cap())  # type: ignore[arg-type]


def test_wrap_module_alias() -> None:
    wrapped = wrap_module(_boom_agent)
    assert wrapped({}) == EMERGENCY_ACTION
