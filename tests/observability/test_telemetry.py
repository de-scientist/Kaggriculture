"""Tests for the telemetry aggregator."""
from __future__ import annotations

from agent.observability import get_metrics, reset_metrics, reset_telemetry
from agent.observability.telemetry import get_telemetry


def test_record_decision_updates_count_and_latency() -> None:
    telem = reset_telemetry()
    telem.record_decision(10.0, strategy="baseline")
    telem.record_decision(20.0, strategy="baseline")
    snap = telem.snapshot()
    assert snap.decisions == 2
    assert snap.average_latency_ms == 15.0
    assert snap.longest_decision_ms == 20.0
    assert snap.strategy_usage["baseline"] == 2


def test_decisions_property() -> None:
    telem = reset_telemetry()
    assert telem.decisions == 0
    telem.record_decision(5.0)
    assert telem.decisions == 1


def test_record_failed_validation() -> None:
    telem = reset_telemetry()
    telem.record_failed_validation()
    telem.record_failed_validation()
    assert telem.snapshot().failed_validations == 2


def test_record_exception() -> None:
    telem = reset_telemetry()
    telem.record_exception("AttributeError")
    telem.record_exception("AttributeError")
    telem.record_exception("ValueError")
    snap = telem.snapshot()
    assert snap.exception_counts == {"AttributeError": 2, "ValueError": 1}


def test_record_strategy() -> None:
    telem = reset_telemetry()
    telem.record_strategy("utility")
    assert telem.snapshot().strategy_usage == {"utility": 1}


def test_average_latency_empty_is_zero() -> None:
    telem = reset_telemetry()
    assert telem.average_latency_ms() == 0.0


def test_telemetry_propagates_to_metrics() -> None:
    telem = reset_telemetry()
    telem.record_decision(5.0)
    metrics = get_metrics()
    assert metrics.counter("decision_count") == 1.0
    assert metrics.average("decision_time_ms") == 5.0


def test_record_exception_increments_metrics() -> None:
    telem = reset_telemetry()
    telem.record_exception("CropError")
    assert get_metrics().counter("exception_count") == 1.0
    assert get_metrics().counter("exception_count_CropError") == 1.0


def test_report_shape() -> None:
    telem = reset_telemetry()
    telem.record_decision(1.0)
    report = telem.report()
    for key in ("decisions", "average_latency_ms", "longest_decision_ms",
                "failed_validations", "strategy_usage", "exception_counts",
                "uptime_seconds"):
        assert key in report


def test_reset_clears_state() -> None:
    telem = reset_telemetry()
    telem.record_decision(1.0)
    telem.record_exception("X")
    telem.reset()
    snap = telem.snapshot()
    assert snap.decisions == 0
    assert snap.exception_counts == {}


def test_get_telemetry_returns_cached() -> None:
    reset_telemetry()
    assert get_telemetry() is get_telemetry()
