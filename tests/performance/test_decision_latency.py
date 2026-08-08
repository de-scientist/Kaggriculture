"""Performance regression tests (chapter 9).

Verifies that decision latency stays within configured budgets.
"""
from __future__ import annotations

import statistics
import time

import pytest

from agent.agent import agent
from agent.observability import PerformanceBudget, get_metrics

from tests.fixtures.observations import minimal_observation


OBS = minimal_observation()


PERFORMANCE_BENCHMARK_COUNT = 100


class TestDecisionLatency:
    def test_average_decision_latency_within_budget(self) -> None:
        latencies = []
        for step in range(PERFORMANCE_BENCHMARK_COUNT):
            obs = dict(OBS)
            obs["step"] = step
            start = time.perf_counter()
            agent(obs)
            latencies.append((time.perf_counter() - start) * 1000)

        avg = statistics.mean(latencies)
        assert avg < 50.0, f"Average decision latency {avg:.2f}ms exceeds 50ms budget"

    def test_p95_decision_latency_within_budget(self) -> None:
        latencies = []
        for step in range(PERFORMANCE_BENCHMARK_COUNT):
            obs = dict(OBS)
            obs["step"] = step
            start = time.perf_counter()
            agent(obs)
            latencies.append((time.perf_counter() - start) * 1000)

        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        assert p95 < 200.0, f"P95 decision latency {p95:.2f}ms exceeds 200ms budget"

    def test_no_memory_leak_over_many_decisions(self) -> None:
        import tracemalloc

        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()

        for step in range(500):
            obs = dict(OBS)
            obs["step"] = step
            agent(obs)

        snapshot_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats_before = snapshot_before.statistics("lineno")
        stats_after = snapshot_after.statistics("lineno")

        before_total = sum(s.size for s in stats_before)
        after_total = sum(s.size for s in stats_after)

        growth = after_total - before_total
        assert growth < 50 * 1024 * 1024, (
            f"Memory grew by {growth / 1024 / 1024:.1f} MB over 500 decisions, "
            "possible leak"
        )


class TestBudgetEnforcement:
    def test_performance_budget_config_exists(self) -> None:
        budget = PerformanceBudget({"decision_time_ms": {"target": 50, "critical": 200}})
        result = budget.check("decision_time_ms", 30.0)
        assert result.status.value == "ok"

    def test_performance_budget_warning(self) -> None:
        budget = PerformanceBudget({"decision_time_ms": {"target": 50, "critical": 200}})
        result = budget.check("decision_time_ms", 60.0)
        assert result.status.value == "warning"

    def test_performance_budget_critical(self) -> None:
        budget = PerformanceBudget({"decision_time_ms": {"target": 50, "critical": 200}})
        result = budget.check("decision_time_ms", 250.0)
        assert result.status.value == "critical"
