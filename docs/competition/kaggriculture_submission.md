# Kaggriculture Submission Guide

## Official Entry Point

The official Kaggle Competition requires:

- A file named `main.py` at the root of the submission
- A function named `agent` that accepts an observation dict and returns
  an action dict

```python
# main.py
def agent(obs: dict) -> dict:
    ...
```

This is verified by the official Kaggle documentation (AGENTS.md).

## Action Format

The agent must return:

```python
{
    "farmer": [op, ...args],          # one main-farmer op
    "hands": [[op, ...args], ...],    # one op per hired hand
    "market": [[op, ...args], ...],   # ordered market orders
}
```

### Farmer/Hand Operations

- **Movement:** `NORTH`, `SOUTH`, `EAST`, `WEST`, `PASS`
- **Shed/Inventory:** `PICKUP <item> [n]`, `PLACE <item> [n]`, `DROP`
- **Plants:** `PLANT <crop>`, `WATER`, `HARVEST`, `FERTILIZE`
- **Animals:** `BUILD_COOP`, `BUILD_PASTURE`, `FEED`, `COLLECT_FERTILIZER`, `CARE`
- **Terrain:** `DIG`

### Market Operations

- `BUY_SEED <crop> <n>`
- `BUY_PRODUCT <item> <n>`
- `BUY_ANIMAL <animal> <n>`
- `SELL <item> <n>`
- `HIRE`
- `BUY_LAND`

## Submission Commands

### Single-file submission

```bash
kaggle competitions submit kaggriculture -f main.py -m "Wheat loop v1"
```

### Multi-file submission

```bash
tar -czf submission.tar.gz main.py agent/
kaggle competitions submit kaggriculture -f submission.tar.gz -m "v1.0.0"
```

## Competition Rules Summary

- **Season:** 720 turns (24 turns/day × 30 days)
- **Players:** 2 (one farm per player)
- **Board:** 10×10 grid, 4 quadrants (NW starts unlocked)
- **Starting money:** $3,000
- **Shed capacity:** 100 non-seed items
- **Market orders per turn:** 10 (excess is silently dropped)
- **Win condition:** Most coins at end of season
