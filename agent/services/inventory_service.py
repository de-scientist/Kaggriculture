from agent.domain import inventory as inventory_domain


SHEED_CAPACITY = 100


def add_item(inventory: dict, item: str, count: int) -> bool:
    current = inventory.get(item, 0)
    if current + count > SHEED_CAPACITY:
        return False
    inventory[item] = current + count
    return True


def remove_item(inventory: dict, item: str, count: int) -> bool:
    current = inventory.get(item, 0)
    if current < count:
        return False
    inventory[item] = current - count
    return True


def available(inventory: dict, item: str) -> int:
    return inventory.get(item, 0)


def space_remaining(inventory: dict) -> int:
    total = sum(inventory.values())
    return max(0, SHEED_CAPACITY - total)