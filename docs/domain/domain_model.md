# Domain Model

## Overview

The domain layer (`agent/domain/`) contains pure data models with no
infrastructure dependencies. All objects are immutable value objects.
The root aggregate is `GameState`, which composes `Farm`, `Market`,
`Town`, `Season`, `Inventory`, and `Player`.

## Class Hierarchy

```
GameState (root aggregate)
├── Farm
│   ├── Tile (dict[Position, Tile])
│   │   ├── Crop (optional)
│   │   ├── Animal (optional, in COOP/PASTURE tiles)
│   │   └── Weed (optional)
│   ├── Quadrant (list of unlocked quadrant names)
│   ├── Building (list of building names)
│   └── Worker (list of Worker objects)
├── Market (inventory, prices)
├── Town (unlocked shops)
├── Season (day, turn, total_turns)
├── Inventory (item counts)
├── Wallet (money)
└── Player (index)
```

## Immutability

All domain objects follow the immutable value-object pattern:

- Methods that would mutate state instead return a new instance.
- Properties are read-only.
- `__slots__` is used to prevent accidental attribute creation.

Example:

```python
crop = Crop(crop_type="WHEAT", planted_day=0)
watered = crop.water()   # returns a new Crop, crop unchanged
assert crop.watered_today is False
assert watered.watered_today is True
```

## Key Concepts

- **Position**: (x, y) grid coordinates within a quadrant (0–4) or
  full board (0–9).
- **Quadrant**: NW, NE, SW, SE — each 5×5. NW starts unlocked.
- **Tile**: Can be empty (None), a plant, a weed, or a structure
  (COOP/PASTURE with optional animal).
- **Worker**: The main farmer plus hired hands. Each acts independently
  every turn.
- **Season**: Tracks day (0–29) and hour/turn (0–23) within the 720-turn
  season.
