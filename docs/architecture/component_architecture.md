# Component Architecture

## Component Map

| Component | Module | Responsibility |
|---|---|---|
| `ObservationAdapter` | `agent/adapters/observation_adapter.py` | Parse raw Kaggle observation → GameState |
| `ActionAdapter` | `agent/adapters/action_adapter.py` | Serialize internal action → Kaggle action dict |
| `DecisionEngine` | `agent/decision/decision_engine.py` | Orchestrate candidate generation, filtering, validation, ranking |
| `DecisionContext` | `agent/decision/decision_engine.py` | Immutable context object passed to the decision engine |
| `GameState` | `agent/domain/game_state.py` | Root aggregate of the domain model |
| `Farm` | `agent/domain/farm.py` | Player farm: tiles, quadrants, buildings, workers, money |
| `Tile` | `agent/domain/tile.py` | Grid tile: empty, plant, weed, structure |
| `Crop` | `agent/domain/crop.py` | Crop lifecycle: growth stage, watering, harvest |
| `Animal` | `agent/domain/animal.py` | Animal lifecycle: feeding, care, production, fertilizer |
| `Worker` | `agent/domain/worker.py` | Farm worker: position, movement, task assignment |
| `Market` | `agent/domain/market.py` | Market state: inventory, prices |
| `Season` | `agent/domain/season.py` | Turn/day tracking, remaining turns |
| `Inventory` | `agent/domain/inventory.py` | Item inventory with capacity tracking |
| `Wallet` | `agent/domain/wallet.py` | Money tracking |
| `Quadrant` | `agent/domain/quadrant.py` | Land quadrant unlock state |
| `Town` | `agent/domain/town.py` | Town demand and shop state |
| `Position` | `agent/domain/position.py` | Grid position (x, y) |
| `Player` | `agent/domain/player.py` | Player data (index, etc.) |
| `StrategyEngine` | `agent/strategies/strategy_engine.py` | Score and rank candidate actions |
| `BaselineStrategy` | `agent/strategies/baseline_strategy.py` | Deterministic rule-based strategy |
| `CandidateAction` | `agent/decision/candidate_actions.py` | Data class for candidate actions |
| `CropService` | `agent/services/crop_service.py` | Crop lifecycle operations |
| `AnimalService` | `agent/services/animal_service.py` | Animal lifecycle operations |
| `WorkerService` | `agent/services/worker_service.py` | Worker movement and task assignment |
| `InventoryService` | `agent/services/inventory_service.py` | Inventory capacity and reservations |
| `MarketService` | `agent/services/market_service.py` | Market price computation |
| `PlanningService` | `agent/services/planning_service.py` | Task scheduling and priority |
| `ValidationService` | `agent/services/validation_service.py` | Action legality checking |
| `LandService` | `agent/services/land_service.py` | Quadrant unlocking logic |
| `ActionGenerator` | `agent/decision/action_generator.py` | Generate candidate actions |
| `ActionFilter` | `agent/decision/action_filter.py` | Filter illegal actions |
| `ActionValidator` | `agent/decision/action_validator.py` | Validate action legality |
| `Ranker` | `agent/decision/ranker.py` | Select best action from ranked candidates |
| `Settings` | `agent/config/settings.py` | Application configuration |
| `Telemetry` | `agent/observability/telemetry.py` | Recording decisions, exceptions, metrics |
| `Tracer` | `agent/observability/tracing.py` | Decision tracing and correlation |
| `PerformanceBudget` | `agent/observability/performance.py` | Performance budget enforcement |

## Dependency Direction

```
Kaggle Environment
  → main.py
    → agent.agent
      → agent.adapters  (input: raw obs, output: GameState)
      → agent.decision  (input: GameState, output: internal action)
        → agent.strategies  (scoring model)
        → agent.services    (business logic)
          → agent.domain      (pure models)
      → agent.adapters  (input: internal action, output: Kaggle action dict)
      → agent.observability (telemetry, tracing)
      → agent.config (settings)
      → agent.logging (structured logging)
      → agent.exceptions (error handling)
```

All dependencies point inward toward the domain layer. The domain layer
has no dependencies on outer layers.
