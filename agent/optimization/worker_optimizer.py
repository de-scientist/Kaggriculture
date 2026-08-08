"""Stage 2 — Worker Scheduling Optimization.

Optimizes worker task assignment and scheduling using economic value
ranking and critical path analysis.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WorkerTask:
    """A task assigned to a worker."""

    worker_id: str
    action_type: str
    target_position: tuple[int, int] | None
    estimated_value: float
    estimated_cost: float
    priority: int
    reason: str

    @property
    def net_value(self) -> float:
        return self.estimated_value - self.estimated_cost

    @property
    def value_per_turn(self) -> float:
        if self.estimated_cost < 0:
            return float("inf")
        return self.net_value


@dataclass
class WorkerOptimizer:
    """Assigns workers to tasks to maximize value per turn.

    Uses a greedy assignment algorithm that prioritizes high-value
    tasks for available workers.
    """

    max_tasks_per_worker: int = 1

    def assign_tasks(
        self,
        worker_count: int,
        available_tasks: list[WorkerTask],
    ) -> list[WorkerTask]:
        """Assign tasks to workers greedily by net value."""
        sorted_tasks = sorted(
            available_tasks,
            key=lambda t: (-t.net_value, -t.priority, t.action_type),
        )
        return sorted_tasks[:worker_count * self.max_tasks_per_worker]

    def priority_ranking(self, task: WorkerTask) -> int:
        """Return the priority rank (higher = more urgent)."""
        priority_map = {
            "harvest_mature": 100,
            "water_survival": 90,
            "feed_critical": 85,
            "sell_emergency": 80,
            "harvest": 70,
            "plant": 60,
            "water": 50,
            "fertilize": 45,
            "feed": 40,
            "care": 35,
            "collect_fertilizer": 30,
            "build_coop": 25,
            "build_pasture": 25,
            "buy_seed": 20,
            "buy_animal": 15,
            "buy_land": 10,
            "hire": 5,
            "move": 1,
            "pass": 0,
        }
        return priority_map.get(task.action_type, 0)
