# Crop Service

## Purpose

The crop service manages the full lifecycle of crops: planting, watering, growth, fertilization, and harvesting.

## Responsibilities

- Track crop state per tile (planted day, watered status, yield units, lifespan)
- Apply watering bonus during the bonus window
- Apply fertilizer effects (doubles bonus for 3 days)
- Handle decay after max lifespan
- Calculate harvestable yield
- Manage weed spawning and clearing

## Public Interfaces

### `CropService`

```python
class CropService:
    def plant(self, tile: Tile, crop: str) -> bool: ...
    def water(self, tile: Tile) -> bool: ...
    def fertilize(self, tile: Tile) -> bool: ...
    def harvest(self, tile: Tile) -> HarvestResult: ...
    def update_growth(self, tile: Tile, day: int) -> None: ...
    def clear_weed(self, tile: Tile) -> bool: ...
```

### `CropTracker`

Tracks the state of all crops across the farm.

### `GrowthCalculator`

Calculates growth progress and yield based on crop type and conditions.

### `WateringManager`

Manages watering bonus windows and fertilizer durations.

## Extension Points

- Add new crop types by extending the crop configuration.
- Implement custom yield curves in `GrowthCalculator`.
- Add disease or pest simulation.