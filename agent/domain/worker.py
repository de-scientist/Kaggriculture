from __future__ import annotations

from agent.domain.position import Position


class Worker:
    __slots__ = ("_available", "_id", "_position", "_remaining_movement", "_task")

    def __init__(
        self,
        worker_id: str,
        position: Position,
        max_movement: int = 1,
    ) -> None:
        self._id = worker_id
        self._position = position
        self._task: object | None = None
        self._available = True
        self._remaining_movement = max_movement

    @property
    def id(self) -> str:
        return self._id

    @property
    def position(self) -> Position:
        return self._position

    @property
    def task(self) -> object | None:
        return self._task

    @property
    def available(self) -> bool:
        return self._available

    @property
    def remaining_movement(self) -> int:
        return self._remaining_movement

    def assign_task(self, task: object) -> Worker:
        if not self._available:
            raise ValueError(f"Worker {self._id} is not available")
        w = Worker(
            worker_id=self._id,
            position=self._position,
        )
        w._task = task
        w._available = False
        w._remaining_movement = self._remaining_movement
        return w

    def move(self, new_position: Position) -> Worker:
        if self._remaining_movement <= 0:
            raise ValueError(f"Worker {self._id} has no remaining movement")
        w = Worker(
            worker_id=self._id,
            position=new_position,
        )
        w._task = self._task
        w._available = self._available
        w._remaining_movement = self._remaining_movement - 1
        return w

    def finish_task(self) -> Worker:
        w = Worker(
            worker_id=self._id,
            position=self._position,
        )
        w._task = None
        w._available = True
        w._remaining_movement = self._remaining_movement
        return w

    def reset_daily(self) -> Worker:
        w = Worker(
            worker_id=self._id,
            position=self._position,
        )
        w._task = None
        w._available = True
        w._remaining_movement = 1
        return w

    def __repr__(self) -> str:
        return (
            f"Worker(id={self._id!r}, pos={self._position}, "
            f"available={self._available}, task={self._task})"
        )
