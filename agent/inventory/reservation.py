from typing import Any


def create(inventory: dict[str, Any], item: str, count: int) -> dict[str, Any]:
    return {"item": item, "count": count, "reserved": True}
