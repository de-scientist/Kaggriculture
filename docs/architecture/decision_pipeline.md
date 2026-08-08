# Decision Pipeline

## Pipeline Stages

### Stage 1: Context Construction

The `ObservationAdapter` parses the raw Kaggle observation into a `GameState`.
A `DecisionContext` is then built from the `GameState` plus runtime settings
(seed, strategy name, step/day/hour).

### Stage 2: Candidate Generation

The `ActionGenerator` produces candidate actions based on the current game
state. The Stage 1 baseline generates candidates for:

- Planting (if seeds available and tile is empty)
- Watering (if a plant exists and is not watered today)
- Harvesting (if a mature crop is on the current tile)
- Fertilizing (if in bonus window and fertilizer available)
- Movement (toward nearest target tile)
- Selling (if shed has items)
- Buying seeds (if affordable and needed)
- Hiring (if affordable and beneficial)
- PASS (always available as a fallback)

### Stage 3: Action Filtering

The `ActionFilter` removes candidates that are illegal given the current
game state. For example:

- Cannot plant without seeds
- Cannot harvest an immature crop
- Cannot water an already-watered plant
- Cannot sell items not in shed

### Stage 4: Action Validation

The `ActionValidator` performs deeper validation:

- Movement targets are within bounds
- Tile positions are accessible
- Market orders have valid quantities
- Sufficient funds for market actions

### Stage 5: Strategy Evaluation

The `StrategyEngine` scores each candidate using the weighted scoring model
in `agent/strategies/scoring.py`. Weights include:

| Factor | Weight | Description |
|---|---|---|
| profit | 1.0 | Estimated reward from the action |
| worker_efficiency | 0.3 | Whether a worker is actively used |
| time_efficiency | 0.2 | How time-sensitive the action is |
| inventory_impact | 0.15 | Impact on inventory (selling clears space) |
| market_opportunity | 0.25 | Whether the action exploits market conditions |
| resource_sustainability | 0.1 | Long-term resource health |
| action_cost | -0.5 | Penalizes expensive actions |
| opportunity_cost | -0.2 | Missed alternative opportunities |

### Stage 6: Ranking and Selection

The `Ranker` sorts candidates by score (descending) and breaks ties
deterministically (by action type, then by position). The highest-ranked
candidate is returned.

### Stage 7: Fallback

If no candidates survive filtering, or if the engine encounters an error,
a `PASS` action is returned. This ensures the agent never crashes the
episode.
