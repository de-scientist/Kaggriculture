def apply_fertilizer(tile: dict, current_day: int) -> dict:
    tile["fertilized_until_day"] = current_day + 3
    return tile


def is_fertilized(tile: dict, current_day: int) -> bool:
    return tile.get("fertilized_until_day", -1) >= current_day