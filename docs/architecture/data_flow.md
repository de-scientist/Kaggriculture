# Data Flow

## One Turn Lifecycle

```
Observation Received
        ↓
Observation Validation (schema, fields)
        ↓
GameState Construction (ObservationAdapter.parse)
        ↓
Decision Context built (GameState + Settings + step/day/hour)
        ↓
Candidate Generation (ActionGenerator.generate)
        ↓
Action Filtering (ActionFilter.filter → removes illegal actions)
        ↓
Action Validation (ActionValidator.validate → checks legality)
        ↓
Strategy Evaluation (StrategyEngine.score_action → weighted scoring)
        ↓
Action Ranking (Ranker.rank → deterministic sort)
        ↓
Final Action selected (highest score, deterministic tie-break)
        ↓
Action Serialization (ActionAdapter.convert → Kaggle format)
        ↓
Action returned to Environment
        ↓
Next Observation
```

## Boundary Transformations

### Observation → GameState

The `ObservationAdapter` transforms the raw dict observation:

```
{
  "player": 0,
  "step": 120,
  "day": 5,
  "hour": 0,
  "farms": [{ "money": 3000, "tiles": [...], "farmer": [0,0], ... }],
  "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
  "market": {"inventory": {}, "prices": {}},
  "town": {"unlocked_shops": []}
}
```

into a typed, validated `GameState`:

```
GameState(
  player=0,
  step=120,
  farm=Farm(money=3000, tiles={...}, workers=[Worker(...)]),
  inventory=Inventory(...),
  market=Market(prices={...}),
  town=Town(unlocked_shops=[...]),
  season=Season(day=5, turn=0),
  private={"shed": {...}, "seeds": {...}, ...},
)
```

### GameState → DecisionContext

The `DecisionContext` wraps the `GameState` with additional metadata
required by the decision engine:

```
DecisionContext(
  obs=<raw observation>,
  player=0,
  game_state=GameState(...),
  config=Settings(...),
  step=120,
  day=5,
  hour=0,
  remaining_turns=600,
  strategy_name="baseline",
)
```

### Internal Action → Kaggle Action

The `ActionAdapter` transforms the internal action dict:

```
{
  "farmer": ["PLANT", "WHEAT"],
  "hands": [["PASS"]],
  "market": [["BUY_SEED", "WHEAT", 1], ["SELL", "WHEAT", 5]]
}
```

into the exact Kaggle format (same structure, validated and normalized).

## Key Invariants

- The `GameState` is immutable. Each turn produces a fresh instance.
- The internal action dict always has keys: `farmer`, `hands`, `market`.
- The `farmer` action is always a non-empty list.
- The `hands` action is one entry per hired hand.
- The `market` action is a list of valid market orders.
