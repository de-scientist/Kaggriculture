from typing import Any


def can_harvest(tile: dict[str, Any], current_day: int) -> bool:
    if tile is None or not isinstance(tile, dict):
        return False
    age = current_day - int(tile.get("planted_day", -1))
    return age >= 2
