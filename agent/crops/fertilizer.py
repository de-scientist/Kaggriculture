from typing import Any


def apply_fertilizer(tile: dict[str, Any], current_day: int) -> dict[str, Any]:
    tile["fertilized_until_day"] = current_day + 3
    return tile


def is_fertilized(tile: dict[str, Any], current_day: int) -> bool:
    return int(tile.get("fertilized_until_day", -1)) >= current_day
