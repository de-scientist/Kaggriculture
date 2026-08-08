# Crop System

## Overview

Crops are grown on farm tiles. Each crop has a type (WHEAT, CARROT, TOMATO,
STRAWBERRY, MELON), a growth lifecycle, and specific yield characteristics.

## Crop Types

| Crop | Type | Seed Cost | First Yield Day | Max Yield Day | Base Price |
|---|---|---|---|---|---|
| Wheat | One-time | 10 | 2 | 4 | ~10 |
| Carrot | One-time | 20 | 3 | 6 | ~20 |
| Tomato | Ongoing | 30 | 2 | — | ~25 |
| Strawberry | Ongoing | 40 | 1 | — | ~50 |
| Melon | One-time | 50 | 5 | 10 | ~80 |

## Lifecycle

1. **Plant** — `PLANT <crop>` consumes a seed from the player's seed
   inventory. The planting day counts as day 0.
2. **Water** — Must be watered daily. The planting day counts as the first
   unwatered day. Two consecutive missed end-of-day refreshes turn crops
   into weeds.
3. **Grow** — Daily growth increases yield units. Watering during the
   bonus window adds 1 unit per day. Fertilizing doubles the bonus for 3 days.
4. **Harvest** — `HARVEST` collects the crop when mature (yield > 0).
   One-time crops are removed after harvest. Ongoing crops continue
   producing.

## Watering Bonus

For one-time crops, watering during the bonus window
(starting at `ceil(max_yield_day / 2)`) adds 1 unit per day to the
harvestable yield. `FERTILIZE` doubles this bonus for 3 days.

For ongoing crops, scheduled production yields 1 by default, doubled to 2
if both fertilized and watered that day.

## Decay

Once a crop passes its max lifespan, `yield_units` drops by 1 every other
turn until 0, at which point the tile becomes a weed.

## Domain Model

`Crop` (`agent/domain/crop.py`) tracks:

| Field | Description |
|---|---|
| `crop_type` | Crop name string |
| `planted_day` | Day the crop was planted |
| `watered_today` | Whether watered this turn |
| `consecutive_unwatered` | Consecutive days without water |
| `yield_units` | Harvestable yield |
| `max_lifespan_step` | Turn after which decay begins |
| `fertilized_until_day` | Day until which fertilizer is active |
