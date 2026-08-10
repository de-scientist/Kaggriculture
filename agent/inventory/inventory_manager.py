from typing import Any

from agent.inventory import reservation


def track(inventory: dict[str, Any]) -> dict[str, Any]:
    return inventory


def reserve(inventory: dict[str, Any], item: str, count: int) -> dict[str, Any]:
    return reservation.create(inventory, item, count)
