def can_harvest(tile: dict, current_day: int) -> bool:
    if tile is None or not isinstance(tile, dict):
        return False
    age = current_day - tile.get("planted_day", -1)
    return age >= 2
