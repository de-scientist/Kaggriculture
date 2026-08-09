from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionTrace:
    observation_id: str
    economic_state: dict
    candidates: list[dict]
    forecasts: dict
    expected_values: dict
    risk: float
    strategy: str
    planning_depth: int
    search_nodes: int
    selected_plan: Plan | None
    selected_action: dict | None
    confidence: float
    execution_time_ms: float
    timestamp: str


class DecisionTraceManager:
    """Records structured decision traces for debugging and research."""

    def __init__(self):
        self._traces: list[DecisionTrace] = []
        self._trace_id = 0

    def record(
        self,
        observation_id: str,
        economic_state: dict,
        candidates: list[dict],
        forecasts: dict,
        expected_values: dict,
        risk: float,
        strategy: str,
        planning_depth: int,
        search_nodes: int,
        selected_plan: Plan | None,
        selected_action: dict | None,
        confidence: float,
        execution_time_ms: float,
    ) -> DecisionTrace:
        trace = DecisionTrace(
            observation_id=observation_id,
            economic_state=economic_state,
            candidates=candidates,
            forecasts=forecasts,
            expected_values=expected_values,
            risk=risk,
            strategy=strategy,
            planning_depth=planning_depth,
            search_nodes=search_nodes,
            selected_plan=selected_plan,
            selected_action=selected_action,
            confidence=confidence,
            execution_time_ms=execution_time_ms,
            timestamp=str(__import__("time").time()),
        )
        self._traces.append(trace)
        return trace

    def get_last_trace(self) -> DecisionTrace | None:
        return self._traces[-1] if self._traces else None

    def get_all_traces(self) -> list[DecisionTrace]:
        return list(self._traces)