from typing import Any

SHEED_CAPACITY = 100


def remaining(current: dict[str, Any]) -> int:
    total = sum(current.values())
    return max(0, SHEED_CAPACITY - total)


def can_fit(current: dict[str, Any], item: str, count: int) -> bool:
    return remaining(current) >= count
