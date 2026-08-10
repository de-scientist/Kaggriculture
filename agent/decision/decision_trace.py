from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionTrace:
    """Structured record of a single decision turn.

    The decision engine builds a trace incrementally as each pipeline phase
    completes (candidate generation, validation, ranking, selection) and then
    marks it complete once the action has been selected and recorded.
    """

    step: int = 0
    day: int = 0
    strategy_name: str = "baseline"
    player: int = 0
    observation_id: str = ""
    economic_state: dict[str, Any] = field(default_factory=dict)
    candidates: list[dict[str, Any]] = field(default_factory=list)
    forecasts: dict[str, Any] = field(default_factory=dict)
    expected_values: dict[str, Any] = field(default_factory=dict)
    risk: float = 0.0
    strategy: str = "baseline"
    planning_depth: int = 0
    search_nodes: int = 0
    selected_plan: Any = None
    selected_action: dict[str, Any] | None = None
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    timestamp: str = ""
    failure: str | None = None

    def record_candidates(self, count: int) -> None:
        self.planning_depth = count
        self.search_nodes = count

    def record_validation(self, validated: list[Any]) -> None:
        self.expected_values = {
            getattr(v.action, "id", str(i)): getattr(v, "is_valid", False)
            for i, v in enumerate(validated)
        }

    def record_ranking(self, scored: list[Any]) -> None:
        self.expected_values = {
            getattr(s.action, "id", str(i)): getattr(s, "score", 0.0) for i, s in enumerate(scored)
        }

    def record_final(self, selected: Any) -> None:
        self.selected_action = {
            "action_type": getattr(selected, "action_type", "pass"),
            "id": getattr(selected, "id", ""),
        }

    def record_failure(self, message: str) -> None:
        self.failure = message
        if not self.timestamp:
            self.timestamp = str(time.time())

    def mark_complete(self, start: float) -> None:
        self.execution_time_ms = (time.perf_counter() - start) * 1000.0
        if not self.timestamp:
            self.timestamp = str(time.time())


class DecisionTraceManager:
    """Records structured decision traces for debugging and research."""

    def __init__(self) -> None:
        self._traces: list[DecisionTrace] = []

    def record(
        self,
        observation_id: str = "",
        economic_state: dict[str, Any] | None = None,
        candidates: list[dict[str, Any]] | None = None,
        forecasts: dict[str, Any] | None = None,
        expected_values: dict[str, Any] | None = None,
        risk: float = 0.0,
        strategy: str = "baseline",
        planning_depth: int = 0,
        search_nodes: int = 0,
        selected_plan: Any = None,
        selected_action: dict[str, Any] | None = None,
        confidence: float = 0.0,
        execution_time_ms: float = 0.0,
        *,
        step: int = 0,
        day: int = 0,
        strategy_name: str = "baseline",
        player: int = 0,
    ) -> DecisionTrace:
        trace = DecisionTrace(
            step=step,
            day=day,
            strategy_name=strategy_name,
            player=player,
            observation_id=observation_id,
            economic_state=dict(economic_state or {}),
            candidates=list(candidates or []),
            forecasts=dict(forecasts or {}),
            expected_values=dict(expected_values or {}),
            risk=risk,
            strategy=strategy,
            planning_depth=planning_depth,
            search_nodes=search_nodes,
            selected_plan=selected_plan,
            selected_action=selected_action,
            confidence=confidence,
            execution_time_ms=execution_time_ms,
            timestamp=str(time.time()),
        )
        self._traces.append(trace)
        return trace

    def get_last_trace(self) -> DecisionTrace | None:
        return self._traces[-1] if self._traces else None

    def get_all_traces(self) -> list[DecisionTrace]:
        return list(self._traces)
