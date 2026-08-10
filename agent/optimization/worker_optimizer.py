from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class WorkerTask:
    task_type: str
    priority: int
    estimated_time: int
    estimated_profit: float
    deadline: int
    worker_type: str = ""


class WorkerOptimizer:
    """Optimizes worker scheduling and task allocation.

    At every decision point, estimates:
    * Worker Availability
    * Worker Task
    * Task Value
    * Task Urgency
    * Task Duration
    * Opportunity Cost
    """

    def __init__(self):
        self._worker_data = {}

    def optimize(
        self,
        available_workers: int,
        current_actions: list[str],
        available_turns: int,
    ) -> dict[str, Any]:
        best = None
        best_score = -float("inf")
        for worker_type, data in self._worker_data.items():
            score = self._evaluate_worker(
                worker_type=worker_type,
                available_workers=available_workers,
                current_actions=current_actions,
                available_turns=available_turns,
                data=data,
            )
            if score > best_score:
                best_score = score
                best = data
        return best

    def _evaluate_worker(
        self,
        worker_type: str,
        available_workers: int,
        current_actions: list[str],
        available_turns: int,
        data: dict,
    ) -> float:
        return 0.0

    def set_worker_data(self, worker_type: str, data: dict) -> None:
        self._worker_data[worker_type] = data