from typing import Any


def track(tile: dict[str, Any]) -> dict[str, Any]:
    if tile is None or not isinstance(tile, dict):
        return {}
    return tile
