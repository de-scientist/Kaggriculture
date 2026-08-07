"""Performance budget enforcement (chapter 165).

Stage 1 performance targets (configurable via ``settings.performance``):

* Observation parsing: < 5 ms
* Decision Engine: < 20 ms
* Strategy evaluation: < 10 ms
* Action conversion: < 2 ms
* Total decision: comfortably below Kaggle execution limits (< 500 ms)

A :class:`PerformanceBudget` checks measured durations against these thresholds
and classifies results as ``ok`` / ``warning`` / ``critical``.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from agent.exceptions.strategy import StrategyError


class BudgetStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"

    def __bool__(self) -> bool:
        return self is BudgetStatus.OK


@dataclass
class BudgetResult:
    component: str
    duration_ms: float
    budget_ms: float
    status: BudgetStatus
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "duration_ms": round(self.duration_ms, 3),
            "budget_ms": self.budget_ms,
            "status": self.status.value,
            "message": self.message,
        }


# Default Stage 1 budgets (ms) per the chapter specification.
DEFAULT_BUDGETS: dict[str, dict[str, float]] = {
    "observation_parsing_ms": {"target": 5, "component": "ObservationAdapter"},
    "decision_engine_ms": {"target": 20, "component": "DecisionEngine"},
    "strategy_evaluation_ms": {"target": 10, "component": "StrategyManager"},
    "action_conversion_ms": {"target": 2, "component": "ActionSerializer"},
    "total_decision_ms": {"target": 500, "component": "Total"},
}


class PerformanceBudget:
    """Checks measured durations against configured performance budgets."""

    def __init__(
        self,
        budgets: dict[str, Any] | None = None,
        *,
        warning_ms: float | None = None,
        failure_ms: float | None = None,
    ) -> None:
        self._targets: dict[str, float] = {}
        self._components: dict[str, str] = {}
        self._warning_ms = warning_ms
        self._failure_ms = failure_ms
        if budgets:
            for key, value in budgets.items():
                if key in ("warning_threshold_ms", "failure_threshold_ms"):
                    continue
                if isinstance(value, dict) and "target" in value:
                    self._targets[key] = float(value["target"])
                    self._components[key] = value.get("component", key)
                elif isinstance(value, (int, float)) and key.endswith("_ms"):
                    self._targets[key] = float(value)
                    self._components[key] = key.replace("_ms", "")
            self._warning_ms = self._warning_ms or budgets.get("warning_threshold_ms")
            self._failure_ms = self._failure_ms or budgets.get("failure_threshold_ms")
        else:
            for key, meta in DEFAULT_BUDGETS.items():
                self._targets[key] = meta["target"]
                self._components[key] = meta["component"]
            self._warning_ms = self._warning_ms or 800
            self._failure_ms = self._failure_ms or 1500

    def check(self, component_key: str, duration_ms: float) -> BudgetResult:
        budget = self._targets.get(component_key)
        label = self._components.get(component_key, component_key)
        if budget is None:
            return BudgetResult(
                component=label, duration_ms=duration_ms, budget_ms=-1,
                status=BudgetStatus.OK, message="no budget defined",
            )
        if duration_ms >= self._failure_ms:
            status = BudgetStatus.CRITICAL
        elif duration_ms >= self._warning_ms or duration_ms > budget:
            status = BudgetStatus.WARNING
        else:
            status = BudgetStatus.OK
        message = ""
        if status is BudgetStatus.CRITICAL:
            message = f"{label} exceeded failure threshold ({duration_ms:.1f}ms >= {self._failure_ms}ms)"
        elif status is BudgetStatus.WARNING:
            if duration_ms > budget:
                message = f"{label} exceeded target ({duration_ms:.1f}ms > {budget}ms)"
            else:
                message = f"{label} near warning threshold ({duration_ms:.1f}ms >= {self._warning_ms}ms)"
        return BudgetResult(
            component=label, duration_ms=duration_ms, budget_ms=budget,
            status=status, message=message,
        )

    def enforce(self, component_key: str, duration_ms: float) -> BudgetResult:
        """Check and raise :class:`StrategyError` on critical violations."""
        result = self.check(component_key, duration_ms)
        if result.status is BudgetStatus.CRITICAL:
            raise StrategyError(
                f"Performance budget exceeded for {result.component}: "
                f"{duration_ms:.1f}ms > {self._failure_ms}ms",
                context={"component": result.component, "duration_ms": duration_ms},
            )
        return result

    def all_targets(self) -> dict[str, float]:
        return dict(self._targets)


class PerformanceMonitor:
    """Tracks per-step timing and aggregates budget results."""

    def __init__(self, budget: PerformanceBudget) -> None:
        self._budget = budget
        self._current_step_results: list[BudgetResult] = []
        self._history: list[BudgetResult] = []
        self._warning_count = 0
        self._critical_count = 0

    @property
    def budget(self) -> PerformanceBudget:
        return self._budget

    def record(self, component_key: str, duration_ms: float) -> BudgetResult:
        result = self._budget.check(component_key, duration_ms)
        self._current_step_results.append(result)
        if result.status is BudgetStatus.WARNING:
            self._warning_count += 1
        elif result.status is BudgetStatus.CRITICAL:
            self._critical_count += 1
        return result

    def step_results(self) -> list[BudgetResult]:
        return list(self._current_step_results)

    def reset_step(self) -> None:
        self._history.extend(self._current_step_results)
        self._current_step_results.clear()

    @property
    def warning_count(self) -> int:
        return self._warning_count

    @property
    def critical_count(self) -> int:
        return self._critical_count

    def report(self) -> dict[str, Any]:
        return {
            "targets": self._budget.all_targets(),
            "warnings": self._warning_count,
            "criticals": self._critical_count,
            "last_step": [r.to_dict() for r in self._current_step_results],
        }
