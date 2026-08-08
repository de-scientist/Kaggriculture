# GameState

## Overview

`GameState` (`agent/domain/game_state.py`) is the root aggregate of the
domain layer. It represents the complete internal state of one player's
perspective at a single turn.

## Fields

| Field | Type | Description |
|---|---|---|
| `player` | `int` | Player index (0 or 1) |
| `farm` | `Farm` | Player's farm: tiles, quadrants, workers, money |
| `inventory` | `Inventory` | Shed inventory (non-seed items) |
| `market` | `Market` | Shared market state |
| `town` | `Town` | Town shop demand state |
| `season` | `Season` | Day/turn tracking |
| `weather` | `Weather` | Weather state (if applicable) |
| `opponent` | `Player` | Opponent public data |
| `private` | `dict` | Private player data (seeds, shed, inventories) |
| `step` | `int` | Absolute step number (0–719) |

## Key Methods

| Method | Description |
|---|---|
| `current_day()` | Current in-game day (0–29) |
| `current_turn()` | Current turn within the day (0–23) |
| `remaining_turns()` | Turns remaining in the season |
| `remaining_days()` | Days remaining in the season |
| `available_money()` | Current bank balance |
| `available_workers()` | List of available workers |
| `current_market()` | Current market state |
| `advance_turn()` | Returns a new GameState with season advanced one turn |

## Construction

`GameState` is constructed by the `ObservationAdapter` from the raw
Kaggle observation. The `step` parameter is used to derive the `Season`
if no explicit `Season` is provided.
