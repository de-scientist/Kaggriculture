# Animal System

## Overview

Animals are raised in structures (COOP for Geese, PASTURE for Cows and
Sheep). They produce goods on a schedule and generate fertilizer daily.

## Animal Types

| Animal | Structure | Product | Feed |
|---|---|---|---|
| Goose | Coop | Eggs | Wheat |
| Cow | Pasture | Milk | Wheat |
| Sheep | Pasture | Wool | Wheat |

## Lifecycle

1. **Build Structure** — `BUILD_COOP` or `BUILD_PASTURE` creates the
   required housing on the current tile.
2. **Buy Animal** — `BUY_ANIMAL` purchases an animal from the market.
3. **Place Animal** — `PLACE` puts the animal in a matching structure.
4. **Feed** — Daily feeding prevents escape. Two consecutive missed
   feeds cause escape (unrecoverable).
5. **Care** — `CARE` banks a yield bonus paid out on the next scheduled
   production.
6. **Produce** — At end-of-day, fed animals produce their good and
   generate fertilizer (1 per animal per day).
7. **Collect** — `COLLECT_FERTILIZER` gathers 1 fertilizer per animal.

## Domain Model

`Animal` (`agent/domain/animal.py`) tracks:

| Field | Description |
|---|---|
| `animal_type` | GOOSE, COW, or SHEEP |
| `housing` | COOP, PASTURE, or NONE |
| `hunger` | Current hunger level |
| `health` | Health percentage (starts at 100) |
| `fed_today` | Whether fed this turn |
| `consecutive_unfed` | Consecutive days without feeding |
| `cared_today` | Whether cared for today |
| `pending_care_bonus` | Banked bonus to be paid on next production |
| `fertilizer_available` | Whether fertilizer can be collected |
| `escaped` | Whether the animal has escaped |

## Service Logic

`AnimalService` (`agent/services/animal_service.py`) provides:

- `can_produce(animal)` — checks if animal is fed and alive
- `produce(animal)` — returns (new_animal, bonus_count), sets fertilizer
- `collect_fertilizer(animal)` — returns (new_animal, 1), resets fertilizer
- `feed(animal)` — returns new fed animal, resets consecutive_unfed
- `care(animal)` — returns new cared animal, increments pending_care_bonus
