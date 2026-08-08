"""Tests for the performance budget enforcement."""
from __future__ import annotations

import pytest

from agent.exceptions.strategy import StrategyError
from agent.observability import PerformanceBudget
from agent.observability.performance import (
    DEFAULT_BUDGETS,
    BudgetResult,
    BudgetStatus,
    PerformanceMonitor,
)


def test_default_budgets_contain_targets() -> None:
    assert DEFAULT_BUDGETS["total_decision_ms"]["target"] == 500
    assert DEFAULT_BUDGETS["observation_parsing_ms"]["component"] == "ObservationAdapter"


def test_check_ok_within_budget() -> None:
    perf = PerformanceBudget()
    result = perf.check("total_decision_ms", 10.0)
    assert result.status is BudgetStatus.OK
    assert result.budget_ms == 500


def test_check_warning_over_target() -> None:
    perf = PerformanceBudget({"total_decision_ms": 10})
    result = perf.check("total_decision_ms", 15.0)
    assert result.status is BudgetStatus.WARNING
    assert "target" in result.message


def test_check_no_budget_defined() -> None:
    perf = PerformanceBudget()
    result = perf.check("unknown_key", 5.0)
    assert result.status is BudgetStatus.OK
    assert result.message == "no budget defined"


def test_enforce_raises_on_critical() -> None:
    perf = PerformanceBudget({"total_decision_ms": 10}, failure_ms=50.0)
    with pytest.raises(StrategyError):
        perf.enforce("total_decision_ms", 100.0)


def test_enforce_passes_under_failure_threshold() -> None:
    perf = PerformanceBudget({"total_decision_ms": 10}, warning_ms=15.0, failure_ms=50.0)
    result = perf.enforce("total_decision_ms", 20.0)
    assert result.status is BudgetStatus.WARNING


def test_performance_monitor_aggregates() -> None:
    perf = PerformanceBudget({"total_decision_ms": 10})
    monitor = PerformanceMonitor(perf)
    monitor.record("total_decision_ms", 5.0)
    monitor.record("total_decision_ms", 15.0)
    results = monitor.step_results()
    assert len(results) == 2
    assert results[0].status is BudgetStatus.OK
    assert results[1].status is BudgetStatus.WARNING
    monitor.reset_step()
    assert monitor.step_results() == []


def test_performance_monitor_counts_warnings_criticals() -> None:
    perf = PerformanceBudget({"total_decision_ms": 10}, failure_ms=50.0)
    monitor = PerformanceMonitor(perf)
    monitor.record("total_decision_ms", 15.0)  # warning
    monitor.record("total_decision_ms", 100.0)  # critical
    assert monitor.warning_count == 1
    assert monitor.critical_count == 1


def test_budget_result_to_dict_shape() -> None:
    result = BudgetResult(component="Test", duration_ms=1.0, budget_ms=10.0,
                          status=BudgetStatus.OK, message="ok")
    d = result.to_dict()
    assert d["component"] == "Test"
    assert d["status"] == "ok"
