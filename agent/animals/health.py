from typing import Any


def update_health(animal: dict[str, Any]) -> dict[str, Any]:
    if not animal.get("fed_today", False):
        animal["consecutive_unfed"] = animal.get("consecutive_unfed", 0) + 1
    else:
        animal["consecutive_unfed"] = 0
    return animal
