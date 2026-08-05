from __future__ import annotations

from agent.domain.inventory import Inventory


def add(inventory: Inventory, item: str, quantity: int) -> Inventory:
    return inventory.add(item, quantity)


def remove(inventory: Inventory, item: str, quantity: int) -> Inventory:
    return inventory.remove(item, quantity)


def reserve(inventory: Inventory, item: str, quantity: int) -> Inventory:
    return inventory.reserve(item, quantity)


def release(inventory: Inventory, item: str, quantity: int) -> Inventory:
    return inventory.add(item, quantity)


def available(inventory: Inventory, item: str) -> int:
    return inventory.count(item)


def capacity_remaining(inventory: Inventory) -> int:
    return inventory.space_remaining()


def contains(inventory: Inventory, item: str, quantity: int) -> bool:
    return inventory.has(item, quantity)
