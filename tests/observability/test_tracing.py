"""Tests for the tracing layer."""
from __future__ import annotations

from agent.observability import reset_default_tracer
from agent.observability.tracing import (
    Span,
    Tracer,
    get_active_trace,
    make_correlation_id,
    make_decision_id,
    set_active_trace,
    trace_scope,
)


def test_make_decision_id_deterministic() -> None:
    assert make_decision_id(128) == "d-128"


def test_make_correlation_id_deterministic() -> None:
    cid = make_correlation_id(42, 0)
    assert cid.startswith("c-")
    assert make_correlation_id(42, 0) == cid
    # different seed differs
    assert make_correlation_id(7, 0) != cid


def test_make_correlation_id_no_seed() -> None:
    cid = make_correlation_id(None, 1)
    assert cid.startswith("c-")


def test_span_duration_and_finish() -> None:
    span = Span(name="work", start_ms=10.0)
    span.finish(end_ms=25.0)
    assert span.duration_ms == 15.0
    d = span.to_dict()
    assert d["name"] == "work"
    assert d["duration_ms"] == 15.0


def test_span_finish_defaults_to_now() -> None:
    span = Span(name="work", start_ms=10.0)
    span.finish()
    assert span.duration_ms > 0.0


def test_tracer_starts_span_with_attributes() -> None:
    tracer = Tracer()
    span = tracer.start_span("gen", step=1, day=0)
    assert span.name == "gen"
    assert span.attributes["step"] == 1


def test_trace_add_span_and_total_duration() -> None:
    tracer = Tracer(correlation_id="c-1")
    trace = tracer.start_trace(step=3, day=1, player=0, strategy="baseline")
    assert trace.correlation_id == "c-1"
    assert trace.decision_id == "d-3"
    assert trace.strategy == "baseline"
    span = tracer.start_span("phase")
    span.finish(end_ms=span.start_ms + 5.0)
    trace.add_span(span)
    assert trace.total_duration_ms == 5.0
    trace_dict = trace.to_dict()
    assert trace_dict["spans"][0]["name"] == "phase"
    assert trace_dict["correlation_id"] == "c-1"


def test_trace_sets_correlation_id_when_missing() -> None:
    tracer = Tracer()
    trace = tracer.start_trace(step=0, day=0, player=1)
    assert trace.correlation_id.startswith("c-")
    tracer.set_correlation_id("c-explicit")
    trace2 = tracer.start_trace(step=1, day=0, player=1)
    assert trace2.correlation_id == "c-explicit"


def test_set_active_trace_and_get() -> None:
    tracer = Tracer()
    trace = tracer.start_trace(step=5, day=0, player=0)
    set_active_trace(trace)
    assert get_active_trace() is trace
    reset_default_tracer()
    set_active_trace(None)
    assert get_active_trace() is None


def test_trace_scope_sets_and_resets_active_trace() -> None:
    tracer = Tracer()
    trace = tracer.start_trace(step=9, day=2, player=0)
    assert get_active_trace() is None
    with trace_scope(tracer, trace) as active:
        assert active is trace
        assert get_active_trace() is trace
    assert get_active_trace() is None


def test_trace_scope_restores_previous_active_trace() -> None:
    tracer = Tracer()
    trace_a = tracer.start_trace(step=1, day=0, player=0)
    trace_b = tracer.start_trace(step=2, day=0, player=0)
    set_active_trace(trace_a)
    with trace_scope(tracer, trace_b):
        assert get_active_trace() is trace_b
    assert get_active_trace() is trace_a
