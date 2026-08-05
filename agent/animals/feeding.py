def needs_feeding(animal: dict) -> bool:
    return not animal.get("fed_today", False)


def consecutive_misses(animal: dict) -> int:
    return animal.get("consecutive_unfed", 0)


def has_escaped(animal: dict) -> bool:
    return consecutive_misses(animal) >= 2
