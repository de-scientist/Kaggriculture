# Animal Service

## Purpose

The animal service manages the lifecycle of animals: feeding, production, care bonuses, and fertilizer collection.

## Responsibilities

- Track animal state per structure (coop/pasture)
- Enforce daily feeding requirements
- Manage consecutive missed feeding (escape after 2 misses)
- Process care bonuses for next scheduled production
- Collect fertilizer from animals
- Track yield units and production schedules

## Public Interfaces

### `AnimalService`

```python
class AnimalService:
    def feed(self, structure: AnimalStructure) -> bool: ...
    def care(self, structure: AnimalStructure) -> bool: ...
    def collect_fertilizer(self, structure: AnimalStructure) -> int: ...
    def produce(self, structure: AnimalStructure) -> ProductionResult: ...
    def update_health(self, structure: AnimalStructure) -> None: ...
```

### `AnimalTracker`

Tracks the state of all animals across the farm.

### `FeedingManager`

Manages daily feeding state and consecutive missed feeding counts.

### `ProductionManager`

Handles scheduled production and care bonus application.

## Extension Points

- Add new animal types by extending the domain model.
- Implement health deterioration or recovery mechanics.
- Add breeding or offspring mechanics.