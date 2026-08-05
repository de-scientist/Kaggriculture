# Observation Adapter

## Purpose

The observation adapter translates between Kaggle observation objects and internal domain objects. It is the boundary layer between the Kaggle framework and the agent's business logic.

## Responsibilities

- Parse the Kaggle observation dict into internal `GameState`
- Extract player-specific data (farm, private state)
- Extract shared data (market, town)
- Validate observation schema
- Handle missing or unexpected fields gracefully

## Public Interfaces

### `ObservationAdapter`

```python
class ObservationAdapter:
    def adapt(self, obs: dict) -> GameState: ...
```

### `GameState`

The internal representation of the full game state, composed of:
- `PlayerState` (per player)
- `MarketState` (shared)
- `TownState` (shared)

## Extension Points

- Add new field mappings as the Kaggle API evolves.
- Extend validation rules in `ActionValidator`.
- Add backward compatibility for older observation schemas.