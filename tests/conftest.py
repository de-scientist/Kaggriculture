"""Pytest configuration shared across the operational-layer test suite.

Resets the process-wide singletons managed by the operational layer before every
test so that telemetry, metrics, replay, tracing and profiling state never leak
between tests.  The existing domain / service tests do not touch these singletons,
so the autouse fixtures here are safe for the whole suite.
"""
from __future__ import annotations

import pytest

from agent.config import reset_config
from agent.observability import (
    get_metrics,
    get_replay_store,
    get_telemetry,
    reset_default_tracer,
    reset_metrics,
    reset_replay_store,
    reset_telemetry,
)
from agent.observability.profiler import reset_profiler


@pytest.fixture(autouse=True)
def _reset_operational_singletons():
    reset_telemetry()
    reset_metrics()
    reset_replay_store()
    reset_default_tracer()
    reset_profiler()
    reset_config()
    yield
