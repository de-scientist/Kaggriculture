"""Unit tests for Worker Optimizer (Stage 2)."""
from __future__ import annotations

from agent.optimization.worker_optimizer import WorkerOptimizer, WorkerTask


class TestWorkerOptimizer:
    def test_assign_tasks_greedy(self) -> None:
        opt = WorkerOptimizer()
        tasks = [
            WorkerTask("farmer", "harvest", (0, 0), 50.0, 0.0, 5, "harvest wheat"),
            WorkerTask("farmer", "plant", (1, 0), 30.0, 10.0, 3, "plant carrot"),
            WorkerTask("farmer", "water", (2, 0), 10.0, 0.0, 2, "water plant"),
        ]
        assigned = opt.assign_tasks(worker_count=1, available_tasks=tasks)
        assert len(assigned) == 1
        assert assigned[0].action_type == "harvest"  # highest net value

    def test_assign_tasks_multiple_workers(self) -> None:
        opt = WorkerOptimizer()
        tasks = [
            WorkerTask("farmer", "harvest", (0, 0), 50.0, 0.0, 5, "harvest"),
            WorkerTask("hand1", "plant", (1, 0), 30.0, 10.0, 3, "plant"),
            WorkerTask("hand2", "water", (2, 0), 10.0, 0.0, 2, "water"),
            WorkerTask("hand3", "fertilize", (3, 0), 5.0, 2.0, 1, "fert"),
        ]
        assigned = opt.assign_tasks(worker_count=3, available_tasks=tasks)
        assert len(assigned) == 3
        # Highest net values selected
        assert assigned[0].action_type == "harvest"
        assert assigned[1].action_type == "plant"
        assert assigned[2].action_type == "water"

    def test_priority_ranking(self) -> None:
        opt = WorkerOptimizer()
        task = WorkerTask("farmer", "harvest_mature", (0, 0), 50.0, 0.0, 100, "harvest")
        assert opt.priority_ranking(task) == 100

        task2 = WorkerTask("farmer", "pass", (0, 0), 0.0, 0.0, 0, "idle")
        assert opt.priority_ranking(task2) == 0

    def test_worker_task_net_value(self) -> None:
        task = WorkerTask("farmer", "plant", (0, 0), 30.0, 10.0, 3, "plant")
        assert task.net_value == 20.0
