from typing import Any


def order(tasks: list[Any]) -> list[Any]:
    return sorted(tasks, key=lambda t: 0)
