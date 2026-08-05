# Inventory Service

## Purpose

The inventory service manages the player's shed inventory, seed storage, and per-unit field inventories.

## Responsibilities

- Track item counts in the shed (non-seed inventory, cap 100)
- Track seed counts (no cap, never picked up by PICKUP)
- Manage per-unit inventories for farmer and hired hands
- Handle overflow when shed capacity is exceeded
- Support reservation of items for planned actions

## Public Interfaces

### `InventoryService`

```python
class InventoryService:
    def add(self, item: str, count: int) -> bool: ...
    def remove(self, item: str, count: int) -> bool: ...
    def available(self, item: str) -> int: ...
    def shed_space_remaining(self) -> int: ...
```

### `Capacity`

Enforces the shed capacity limit of 100 items.

### `Reservation`

Tracks items reserved for planned future actions.

## Extension Points

- Adjust `shedCapacity` in `configs/strategy.yaml`.
- Add new inventory categories as needed.