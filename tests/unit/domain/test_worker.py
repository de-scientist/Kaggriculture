"""Unit tests for the Worker domain model (chapter 9)."""

from __future__ import annotations

import pytest

from agent.domain.position import Position
from agent.domain.worker import Worker


class TestWorkerConstruction:
    def test_defaults(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        assert worker.id == "farmer"
        assert worker.position == Position(0, 0)
        assert worker.task is None
        assert worker.available is True
        assert worker.remaining_movement == 1

    def test_custom_movement(self) -> None:
        worker = Worker(worker_id="hand1", position=Position(1, 1), max_movement=2)
        assert worker.remaining_movement == 2


class TestWorkerTaskAssignment:
    def test_assign_task_makes_unavailable(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        assigned = worker.assign_task("harvest")
        assert assigned.task == "harvest"
        assert assigned.available is False

    def test_assign_when_busy_raises(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        assigned = worker.assign_task("harvest")
        with pytest.raises(ValueError, match="not available"):
            assigned.assign_task("water")


class TestWorkerMovement:
    def test_move_decreases_remaining(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        moved = worker.move(Position(1, 0))
        assert moved.position == Position(1, 0)
        assert moved.remaining_movement == 0

    def test_move_no_remaining_raises(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        moved = worker.move(Position(1, 0))
        with pytest.raises(ValueError, match="no remaining movement"):
            moved.move(Position(2, 0))

    def test_move_preserves_task_state(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        assigned = worker.assign_task("harvest")
        moved = assigned.move(Position(1, 0))
        assert moved.task == "harvest"
        assert moved.available is False


class TestWorkerFinish:
    def test_finish_task_releases(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        assigned = worker.assign_task("harvest")
        finished = assigned.finish_task()
        assert finished.task is None
        assert finished.available is True


class TestWorkerDailyReset:
    def test_reset_clears_task_and_movement(self) -> None:
        worker = Worker(worker_id="farmer", position=Position(0, 0))
        assigned = worker.assign_task("harvest").move(Position(1, 0))
        reset = assigned.reset_daily()
        assert reset.task is None
        assert reset.available is True
        assert reset.remaining_movement == 1
        assert reset.position == Position(1, 0)
