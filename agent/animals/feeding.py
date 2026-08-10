from typing import Any


def needs_feeding(animal: dict[str, Any]) -> bool:
    return not animal.get("fed_today", False)


def consecutive_misses(animal: dict[str, Any]) -> int:
    return int(animal.get("consecutive_unfed", 0))


def has_escaped(animal: dict[str, Any]) -> bool:
    return consecutive_misses(animal) >= 2
