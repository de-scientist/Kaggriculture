from agent.domain.inventory import Inventory


def add_item(inventory: Inventory, item: str, quantity: int) -> Inventory:
    return inventory.add(item, quantity)


def remove_item(inventory: Inventory, item: str, quantity: int) -> Inventory:
    return inventory.remove(item, quantity)


def reserve_item(inventory: Inventory, item: str, quantity: int) -> Inventory:
    return inventory.reserve(item, quantity)


def available(inventory: Inventory, item: str) -> int:
    return inventory.count(item)


def has_item(inventory: Inventory, item: str, quantity: int) -> bool:
    return inventory.has(item, quantity)


def space_remaining(inventory: Inventory) -> int:
    return inventory.space_remaining()