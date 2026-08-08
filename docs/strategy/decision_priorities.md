# Decision Priorities

## Priority Order

The baseline strategy generates and evaluates actions following this
priority sequence:

| Priority | Action Type | Trigger Condition |
|---|---|---|
| 1 | SELL (emergency) | Shed utilization ≥ 90% |
| 2 | WATER (survival) | Plant has `consecutive_unwatered ≥ 1` |
| 3 | HARVEST | Plant is mature (`yield_units > 0`, age ≥ first_yield_day) |
| 4 | PLANT | Empty tile + available seeds |
| 5 | WATER (growth) | Plant in growing phase, not watered today |
| 6 | FERTILIZE | Plant in bonus window, fertilizer available |
| 7 | FEED | Animal not fed today |
| 8 | CARE | Animal fed, production pending |
| 9 | COLLECT_FERTILIZER | Animal has fertilizer available |
| 10 | HARVEST (animal) | Animal has production ready |
| 11 | BUY_SEED | Seeds depleted, funds available |
| 12 | BUY_ANIMAL | Coop/pasture available, funds > 500 |
| 13 | BUILD_COOP | Near farm, no existing coop |
| 14 | BUILD_PASTURE | Near farm, no existing pasture |
| 15 | HIRE | Fibonacci cost ≤ 3, funds > 100 |
| 16 | BUY_LAND | Funds > 50% of next quadrant cost |
| 17 | MOVE | Navigate toward nearest actionable tile |
| 18 | PASS | No other action possible |

## Scoring Overrides

Certain conditions override the normal scoring:

- **Plant death imminent** (`consecutive_unwatered ≥ 1`): WATER gets
  a +50 bonus.
- **Crop mature**: HARVEST gets a +30 bonus.
- **Shed near capacity** (≥90%): SELL gets a +40 bonus.
- **Animal about to escape** (`consecutive_unfed ≥ 1`): FEED gets
  a +50 bonus.

## Tie-Breaking

When scores are equal, candidates are ranked by:

1. Priority order (lower number = higher priority)
2. Estimated profit (higher = better)
3. Action type alphabetical (deterministic)
4. Position (row-major order)
