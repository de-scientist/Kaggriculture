"""Tests for the metrics collector."""

from __future__ import annotations

from agent.observability import get_metrics, reset_metrics


def test_counter_increment_and_value() -> None:
    metrics = reset_metrics()
    metrics.increment("harvest_count")
    metrics.increment("harvest_count")
    metrics.increment("harvest_count", by=3)
    assert metrics.counter("harvest_count") == 5.0


def test_counter_unknown_is_zero() -> None:
    metrics = reset_metrics()
    assert metrics.counter("does_not_exist") == 0.0


def test_set_counter() -> None:
    metrics = reset_metrics()
    metrics.set_counter("expansion_count", 7.0)
    assert metrics.counter("expansion_count") == 7.0


def test_observe_and_average() -> None:
    metrics = reset_metrics()
    metrics.observe("decision_time_ms", 10.0)
    metrics.observe("decision_time_ms", 20.0)
    assert metrics.average("decision_time_ms") == 15.0


def test_average_unknown_is_zero() -> None:
    metrics = reset_metrics()
    assert metrics.average("nope") == 0.0


def test_gauge_set_and_get() -> None:
    metrics = reset_metrics()
    metrics.set_gauge("land_utilization_ratio", 0.5)
    assert metrics.gauge("land_utilization_ratio") == 0.5
    assert metrics.gauge("missing") is None


def test_record_value_histogram() -> None:
    metrics = reset_metrics()
    for v in (10.0, 20.0, 30.0):
        metrics.record_value("decision_time_ms", v)
    snap = metrics.snapshot()
    assert snap["histograms"]["decision_time_ms"]["count"] == 3


def test_percentile() -> None:
    metrics = reset_metrics()
    for v in (1.0, 2.0, 3.0, 4.0):
        metrics.record_value("latency", v)
    assert metrics.percentile("latency", 50) == 2.0
    assert metrics.percentile("missing", 50) is None


def test_record_decision_time_updates_rate_and_histogram() -> None:
    metrics = reset_metrics()
    metrics.record_decision_time(12.5)
    snap = metrics.snapshot()
    assert snap["average_decision_time_ms"] == 12.5
    assert "decision_time_ms" in snap["histograms"]


def test_snapshot_shape() -> None:
    metrics = reset_metrics()
    metrics.increment("harvest_count")
    snap = metrics.snapshot()
    for key in (
        "counters",
        "averages",
        "gauges",
        "histograms",
        "average_decision_time_ms",
        "total_harvests",
        "total_profit",
        "idle_turns",
        "expansion_count",
    ):
        assert key in snap


def test_record_harvest_profit() -> None:
    metrics = reset_metrics()
    metrics.record_harvest("WHEAT", 5.0, 50.0)
    snap = metrics.snapshot()
    assert snap["total_harvests"] == 1.0
    assert metrics.counter("crop_yield_total") == 5.0
    assert metrics.counter("harvest_count_WHEAT") == 5.0
    assert snap["total_profit"] == 50.0


def test_record_animal_product_profit() -> None:
    metrics = reset_metrics()
    metrics.record_animal_product("COW", 2.0, 30.0)
    assert metrics.counter("animal_product_count") == 1.0
    assert metrics.counter("profit_total") == 30.0


def test_record_idle_turn() -> None:
    metrics = reset_metrics()
    metrics.record_idle_turn()
    metrics.record_idle(turn=3)
    assert metrics.counter("idle_turns") == 4.0


def test_record_land_utilization_ratio() -> None:
    metrics = reset_metrics()
    metrics.record_land_utilization(3, 4)
    assert metrics.gauge("land_utilization_ratio") == 0.75


def test_record_expansion() -> None:
    metrics = reset_metrics()
    metrics.record_expansion("NE")
    assert metrics.counter("expansion_count") == 1.0
    assert metrics.counter("expansion_NE") == 1.0


def test_record_worker_utilization() -> None:
    metrics = reset_metrics()
    metrics.record_worker_utilization(3, 4)
    assert metrics.gauge("worker_utilization_ratio") == 0.75
    assert metrics.counter("worker_busy_units") == 3.0
    assert metrics.counter("worker_total_units") == 4.0


def test_reset_clears_state() -> None:
    metrics = reset_metrics()
    metrics.increment("something")
    metrics.record_value("latency", 1.0)
    metrics.reset()
    assert metrics.snapshot()["counters"] == {}
    assert metrics.snapshot()["histograms"] == {}


def test_get_metrics_returns_cached() -> None:
    reset_metrics()
    first = get_metrics()
    second = get_metrics()
    assert first is second
