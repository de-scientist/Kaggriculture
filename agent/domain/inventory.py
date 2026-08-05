from __future__ import annotations


class Inventory:
    __slots__ = ("_capacity", "_items")

    def __init__(self, capacity: int = 100) -> None:
        self._items: dict[str, int] = {}
        self._capacity = capacity

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def items(self) -> dict[str, int]:
        return dict(self._items)

    def space_remaining(self) -> int:
        return self._capacity - self._total_count()

    def _total_count(self) -> int:
        return sum(self._items.values())

    def add(self, item: str, quantity: int) -> Inventory:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self._total_count() + quantity > self._capacity:
            raise ValueError(
                f"Inventory full: {self._total_count()}/{self._capacity}, "
                f"cannot add {quantity} {item}"
            )
        new_items = dict(self._items)
        new_items[item] = new_items.get(item, 0) + quantity
        inv = Inventory(capacity=self._capacity)
        inv._items = new_items
        return inv

    def remove(self, item: str, quantity: int) -> Inventory:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        current = self._items.get(item, 0)
        if current < quantity:
            raise ValueError(
                f"Insufficient {item}: need {quantity}, have {current}"
            )
        new_items = dict(self._items)
        new_items[item] = current - quantity
        if new_items[item] == 0:
            del new_items[item]
        inv = Inventory(capacity=self._capacity)
        inv._items = new_items
        return inv

    def reserve(self, item: str, quantity: int) -> Inventory:
        return self.remove(item, quantity)

    def has(self, item: str, quantity: int = 1) -> bool:
        return self._items.get(item, 0) >= quantity

    def count(self, item: str) -> int:
        return self._items.get(item, 0)

    def __repr__(self) -> str:
        return f"Inventory(items={self._items}, capacity={self._capacity})"
