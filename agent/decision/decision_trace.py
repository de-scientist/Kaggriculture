from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionTrace:
    step: int = 0
    day: int = 0
    turn: int = 0
    strategy_name: str = "baseline"
    candidate_count: int = 0
    validation_results: list[Any] = field(default_factory=list)
    strategy_scores: dict = field(default_factory=dict)
    ranked_actions: list[Any] = field(default_factory=list)
    final_action: Any = None
    execution_time_ms: float = 0.0
    failures: list[str] = field(default_factory=list)

    def record_candidates(self, count: int) -> None:
        self.candidate_count = count

    def record_validation(self, results: list[Any]) -> None:
        self.validation_results = results

    def record_strategy_scores(self, scores: dict) -> None:
        self.strategy_scores = scores

    def record_ranking(self, actions: list[Any]) -> None:
        self.ranked_actions = actions

    def record_final(self, action: Any) -> None:
        self.final_action = action

    def record_failure(self, reason: str) -> None:
        self.failures.append(reason)

    def mark_complete(self, start_time: float) -> None:
        self.execution_time_ms = (time.perf_counter() - start_time) * 1000
