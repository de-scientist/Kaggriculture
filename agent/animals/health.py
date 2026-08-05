def update_health(animal: dict) -> dict:
    if not animal.get("fed_today", False):
        animal["consecutive_unfed"] = animal.get("consecutive_unfed", 0) + 1
    else:
        animal["consecutive_unfed"] = 0
    return animal