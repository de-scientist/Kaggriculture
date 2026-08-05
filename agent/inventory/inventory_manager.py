from agent.inventory import reservation


def track(inventory: dict) -> dict:
    return inventory


def reserve(inventory: dict, item: str, count: int) -> dict:
    return reservation.create(inventory, item, count)
