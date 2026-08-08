# Market System

## Overview

The market has two sides:

1. **Fixed prices** — Seeds, animals, `BUY_PRODUCT`, and `HIRE` have fixed
   costs set by the game.
2. **Dynamic prices** — Sale prices for harvested produce vary based on
   market inventory.

## Price Function

Price is `base` at the shared starting inventory `I0`, rises as inventory
falls (supply decreases), and falls as inventory grows (supply increases).

Shape functions (per-resource, can differ on each side of I0):

- `linear` — straight proportional change
- `sq` — quadratic (steeper near I0)
- `sqrt` — square root (flatter near I0)
- `log` — logarithmic (very flat near I0)

Premium goods (strawberry, melon, milk, wool) hit by price gluts harder,
driven to the $1 floor. Staples (wheat, carrot) absorb oversupply more
gently.

## Market Orders

Each turn, at most `maxMarketOrdersPerTurn` (default 10) orders are
processed per player. Extras are silently dropped.

### Available Orders

| Order | Description |
|---|---|
| `BUY_SEED` | `[crop, n]` — Buy n seeds of crop |
| `BUY_PRODUCT` | `[item, n]` — Buy n units of item |
| `BUY_ANIMAL` | `[animal, n]` — Buy n animals |
| `SELL` | `[item, n]` — Sell n units of item |
| `HIRE` | `["HIRE"]` — Hire a farm hand |
| `BUY_LAND` | `["BUY_LAND"]` — Unlock a quadrant |

## Town Demand

The town center demands 1 of each non-fertilizer product every
`townCenterSellInterval` turns (default 12), scaling to 2× after day 10
and 4× after day 20.

Additional shops unlock every `townShopUnlockInterval` days (default 3).
Each unlocked shop consumes products every `townShopSellInterval` turns
(default 4, single-product shops consume 2×).

## Domain Model

`Market` (`agent/domain/market.py`) tracks:

| Field | Description |
|---|---|
| `inventory` | Current supply of each product |
| `prices` | Current per-unit sale price (floor 1) |

`MarketService` (`agent/services/market_service.py`) provides:

- `get_sale_price(product)` — Current dynamic sale price
- `get_seed_cost(crop)` — Fixed seed purchase price
- `get_animal_cost(animal)` — Fixed animal purchase price
- `estimate_inventory_change(product, quantity)` — Project market impact
