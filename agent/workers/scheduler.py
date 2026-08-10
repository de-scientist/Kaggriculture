from typing import Any


def schedule_tasks(tasks: list[Any], workers: list[Any]) -> list[Any]:
    assignments: list[Any] = []
    for i, task in enumerate(tasks):
        if i < len(workers):
            assignments.append((workers[i], task))
    return assignments
