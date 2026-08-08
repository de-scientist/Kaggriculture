# Land System

## Overview

Each player has a `boardSize` × `boardSize` grid (default 10×10) divided
into four 5×5 quadrants: NW, NE, SW, SE.

## Quadrant Unlock

- **NW** — Unlocked at game start (free).
- **NE** — Unlock cost: $1,000 (`BUY_LAND`).
- **SW** — Unlock cost: $2,000 (`BUY_LAND`).
- **SE** — Unlock cost: $4,000 (`BUY_LAND`).

## Domain Model

`Quadrant` (`agent/domain/quadrant.py`) tracks:

| Field | Description |
|---|---|
| `name` | NW, NE, SW, or SE |
| `unlocked` | Whether the quadrant is purchased |
| `cost` | Unlock cost in coins |

`Farm` (`agent/domain/farm.py`) tracks `unlocked_quadrants` as a list of
unlocked quadrant names.

## Land Service

`LandService` (`agent/services/land_service.py`) provides:

| Method | Description |
|---|---|
| `can_unlock(farm, quadrant)` | Check if farm can afford to unlock |
| `unlock_cost(quadrant)` | Return unlock cost for a quadrant |
| `next_unlockable(farm)` | Return the next most affordable quadrant |
