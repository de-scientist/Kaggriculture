# Inventory System

## Overview

The farm has two inventory systems:

1. **Shed** — Stores harvested produce, animals, and fertilizer.
   Non-seed inventory cap of 100 items.
2. **Seeds** — Separate inventory slot with no cap. Consumed directly by
   `PLANT` (never picked up via `PICKUP`).

## Shed Inventory

- Cap: 100 non-seed items.
- Items beyond the cap at end-of-day are discarded.
- `PICKUP <item> [n]` — Pick up items from the shed.
- `DROP` — Dump entire carried inventory into the shed (overflow discarded).
- `PLACE <item> [n]` — Place items into the shed or onto matching structures.

## Seed Inventory

- No cap.
- `BUY_SEED <crop> <n>` increases seed count.
- `PLANT <crop>` consumes one seed directly.

## Domain Model

`Inventory` (`agent/domain/inventory.py`) tracks item counts with
capacity enforcement. `InventoryService` provides:

| Method | Description |
|---|---|
| `add(item, count)` | Add items, respecting capacity |
| `remove(item, count)` | Remove items |
| `has(item, count)` | Check if enough items available |
| `reserve(item, count)` | Reserve items, reducing available |
| `release(item, count)` | Release reserved items |
| `total_items()` | Current item count |
| `available_capacity()` | Remaining capacity |

## Per-Worker Carried Inventory

Each worker (farmer and hands) has a small carried inventory
(`private.inventories` in the observation). This is used to carry items
between the shed and the farm.
