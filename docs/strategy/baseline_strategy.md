# Baseline Strategy

## Philosophy

The Stage 1 baseline strategy prioritizes **correctness** and
**reliability** over optimization. It follows a deterministic priority
list and uses a weighted scoring model to rank candidates.

## Action Priorities

1. **Emergency** — Sell items if shed is near capacity (≥90%)
2. **Survival** — Water plants that will die (consecutive_unwatered ≥ 1)
3. **Harvest** — Collect mature crops when yield > 0
4. **Plant** — Plant available seeds on empty tiles
5. **Water** — Water plants in growing/bonus window
6. **Fertilize** — Fertilize crops in bonus window if fertilizer available
7. **Animal Care** — Feed animals, collect production, collect fertilizer
8. **Market** — Buy seeds/land if profitable, hire hands if cheap
9. **Movement** — Navigate toward nearest actionable tile
10. **Fallback** — `PASS`

## Scoring Model

The `score_action` function (`agent/strategies/scoring.py`) computes a
weighted total:

```
total = profit * 1.0
      + worker_efficiency * 0.3
      + time_efficiency * 0.2
      + inventory_impact * 0.15
      + market_opportunity * 0.25
      + resource_sustainability * 0.1
      + action_cost_penalty (-0.5 weight)
      + opportunity_cost_penalty (-0.2 weight)
```

### Weight Details

| Factor | Weight | Range | Rationale |
|---|---|---|---|
| profit | 1.0 | ≥0 | Reward actions that produce immediate coins |
| worker_efficiency | 0.3 | 0.5–1.0 | Prefer actions that use an available worker |
| time_efficiency | 0.2 | 0.3–1.0 | Prioritize time-sensitive actions (harvest/sell) |
| inventory_impact | 0.15 | 0–0.5 | Selling frees shed capacity |
| market_opportunity | 0.25 | 0.2–1.0 | Exploit market price conditions |
| resource_sustainability | 0.1 | 0.5–1.0 | Preserve long-term resource health |
| action_cost_penalty | -0.5 | negative | Discourage expensive actions |
| opportunity_cost_penalty | -0.2 | negative | Account for missed alternatives |

## Economic Assumptions

- Wheat is the most affordable crop (seed cost $10) and provides feed
  for animals.
- Strawberry and melon have high base prices but are volatile (glut
  drives price to $1).
- Animals provide daily production (eggs, milk, wool) plus fertilizer.
- Land expansion is prioritized after day 5 if funds permit.

## Worker Allocation

- The main farmer handles high-priority tasks.
- Hired hands (if available) handle lower-priority tasks like watering
  or movement.
- Workers navigate using simple greedy pathfinding toward the nearest
  actionable tile.

## Crop Decisions

- Plant wheat continuously for steady income and animal feed.
- Plant higher-value crops (carrot, tomato) when funds allow.
- Never plant if insufficient seeds or funds.

## Animal Decisions

- Build coop/pasture before buying animals.
- Feed animals every day (two missed feeds = escape).
- Collect production and fertilizer daily.
- Use CARE before production to bank a bonus.

## Market Behavior

- Sell harvest immediately to free shed capacity.
- Buy seeds when shed has coins and seeds are depleted.
- Buy land when affordable and unclaimed quadrants exist.
- Hire hands only when Fibonacci cost is low (≤3).

## Expansion Behavior

- Unlock NE quadrant first ($1k), then SW ($2k), then SE ($4k).
- Only expand if funds > 50% of unlock cost.

## Fallback Behavior

If no candidates survive filtering, or if any exception occurs:

- Return `{"farmer": ["PASS"], "hands": [], "market": []}`
- Log the error in telemetry
- Record the exception in telemetry

## Limitations

This is a **correctness and reliability baseline**, not an optimized
strategy. It does not include:

- Market forecasting
- Multi-turn planning
- Opponent modeling
- Dynamic reweighting
