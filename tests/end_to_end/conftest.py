"""Conftest for end-to-end tests.

Resets operational singletons before each test to ensure isolation.
"""
from __future__ import annotations

import pytest

from agent.observability import (
    reset_metrics,
    reset_replay_store,
    reset_telemetry,
    reset_default_tracer,
)
from agent.observability.profiler import reset_profiler


@pytest.fixture(autouse=True)
def reset_singletons():
    reset_metrics()
    reset_telemetry()
    reset_replay_store()
    reset_default_tracer()
    reset_profiler()
    yield
