# Worker System

## Overview

Each farm has one main farmer and can hire up to N farm hands per day.
Workers act independently every turn. Each worker can move one tile per
turn and perform one action.

## Hiring

- Hire cost follows a Fibonacci progression:
  `farmHandCostMult * fib(n)` where `n` is the number of hires already
  made today.
- With the default `farmHandCostMult = 1`, costs are:
  `1, 1, 2, 3, 5, 8, 13, 21, ...`
- Costs reset at the start of each day.

## Worker Lifecycle (per day)

1. **Hire** — `HIRE` market order adds a new hand at the next Fibonacci cost.
2. **Assign Tasks** — Each worker (farmer + hands) gets one action per turn.
3. **Reset** — At end of day, workers return to the main farm area,
  movement points reset.

## Domain Model

`Worker` (`agent/domain/worker.py`) tracks:

| Field | Description |
|---|---|
| `id` | Unique worker identifier (e.g., "farmer", "hand_1") |
| `position` | Current `Position(x, y)` on the board |
| `available` | Whether the worker is free for a new task |
| `task` | Assigned task (if any) |
| `remaining_movement` | Movement points left this turn |

## Movement

Workers move one tile per turn using `NORTH`, `SOUTH`, `EAST`, `WEST`.
Movement is bounded by the board size (default 10×10) and unlocked
quadrants.
