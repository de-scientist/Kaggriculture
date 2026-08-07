"""Tests for the optional profiling layer."""
from __future__ import annotations

import pytest

from agent.observability.profiler import (
    Profiler,
    profiled,
    profile_scope,
    reset_profiler,
    is_enabled,
)
from agent.observability import get_profiler


def test_profiler_disabled_by_default_records_nothing() -> None:
    pytest.importorskip("agent.observability.profiler")
    profiler = Profiler(enabled=False)
    profiler.record("op", 5.0)
    assert profiler.samples() == []


def test_profiler_enabled_records_samples() -> None:
    profiler = Profiler(enabled=True)
    profiler.record("op", 5.0, tag="v1")
    samples = profiler.samples()
    assert len(samples) == 1
    assert samples[0].operation == "op"
    assert samples[0].duration_ms == 5.0
    assert samples[0].attributes["tag"] == "v1"


def test_profiler_summary_aggregates() -> None:
    profiler = Profiler(enabled=True)
    profiler.record("a", 2.0)
    profiler.record("a", 4.0)
    profiler.record("b", 10.0)
    summary = profiler.summary()
    assert summary["a"]["count"] == 2
    assert summary["a"]["avg_ms"] == 3.0
    assert summary["b"]["count"] == 1
    assert summary["b"]["total_ms"] == 10.0


def test_profile_scope_records_when_enabled() -> None:
    profiler = Profiler(enabled=True)
    with profile_scope(profiler, "work", unit="cpu"):
        pass
    samples = profiler.samples()
    assert len(samples) == 1
    assert samples[0].operation == "work"
    assert samples[0].attributes["unit"] == "cpu"


def test_profile_scope_noop_when_disabled() -> None:
    profiler = Profiler(enabled=False)
    with profile_scope(profiler, "work"):
        pass
    assert profiler.samples() == []


def test_profiled_decorator_profiles_enabled() -> None:
    profiler = Profiler(enabled=True)

    @profiled("my_func", profiler=profiler)
    def func(a: int, b: int) -> int:
        return a + b

    assert func(2, 3) == 5
    samples = profiler.samples()
    assert len(samples) == 1
    assert samples[0].operation == "my_func"


def test_profiled_decorator_short_circuits_when_disabled() -> None:
    profiler = Profiler(enabled=False)

    @profiled("my_func", profiler=profiler)
    def func(a: int) -> int:
        return a

    assert func(1) == 1
    assert profiler.samples() == []


def test_reset_profiler_clears() -> None:
    profiler = Profiler(enabled=True)
    profiler.record("x", 1.0)
    assert len(profiler.samples()) == 1
    reset_profiler()
    assert len(get_profiler().samples()) == 0


def test_is_enabled_reflects_enable_toggle() -> None:
    from agent.observability import profiler as prof_mod

    original = prof_mod._enabled
    try:
        prof_mod._enabled = False
        assert is_enabled() is False
        prof_mod.enable(True)
        assert is_enabled() is True
        prof_mod.enable(False)
        assert is_enabled() is False
    finally:
        prof_mod._enabled = original
