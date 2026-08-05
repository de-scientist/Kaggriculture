from __future__ import annotations

from typing import Any


def daily_plan(game_state: Any, tasks: list[Any]) -> list[Any]:
    return sorted(tasks, key=lambda t: getattr(t, "priority", 0), reverse=True)


def task_queue(tasks: list[Any]) -> list[Any]:
    return list(tasks)


def next_task(queue: list[Any]) -> Any | None:
    if not queue:
        return None
    return queue[0]


def prioritize(tasks: list[Any], criteria: str) -> list[Any]:
    return sorted(tasks, key=lambda t: getattr(t, criteria, 0), reverse=True)