# System Architecture

## Overview

The Kaggriculture AI agent is a modular, layered system that transforms raw
Kaggle competition observations into validated action dicts. The architecture
separates concerns across six layers:

```
Official Environment (Kaggle)
        ↓
Observation Adapter
        ↓
GameState (Domain)
        ↓
Decision Engine
        ↓
Strategy Engine
        ↓
Services (Business Logic)
        ↓
Domain Model (Crops, Animals, Workers, Market, Land)
        ↓
Action Adapter
        ↓
Official Environment (Kaggle)
```

## Layers

### 1. Official Environment (Kaggle)

The Kaggle competition runtime hosts the Kaggriculture environment and calls
`agent(obs)` each turn (720 turns per episode). It provides the observation
schema and expects the action schema.

**Entry Point:** `main.py` — exposes the `agent` function.

### 2. Observation Adapter

`agent/adapters/observation_adapter.py` translates the raw Kaggle observation
dict into an internal `GameState` domain object. It validates the observation
schema, normalizes fields, and constructs immutable domain models.

### 3. GameState

`agent/domain/game_state.py` is the root aggregate of the domain layer. It
composes `Farm`, `Market`, `Town`, `Season`, `Inventory`, and `Player` into a
single, immutable snapshot of the current game state.

### 4. Decision Engine

`agent/decision/decision_engine.py` orchestrates the decision pipeline:

1. Build a `DecisionContext` from the `GameState`.
2. Generate candidate actions via the strategy's `ActionGenerator`.
3. Filter illegal actions via `ActionFilter`.
4. Validate remaining candidates via `ActionValidator`.
5. Evaluate and rank candidates via `Ranker` using the `StrategyEngine`.
6. Return the highest-ranked action (or a safe `PASS` fallback).

### 5. Strategy Engine

`agent/strategies/` contains replaceable decision algorithms. The Stage 1
baseline strategy uses deterministic rule-based priorities with a
weighted scoring model.

### 6. Services

`agent/services/` contains business-logic services that operate on domain
models:

- `crop_service` — crop lifecycle (growth, watering, harvesting, fertilizing)
- `animal_service` — animal lifecycle (feeding, production, care, collection)
- `worker_service` — worker management (movement, task assignment)
- `inventory_service` — inventory capacity and reservations
- `market_service` — market price computation
- `planning_service` — task scheduling and priority management
- `validation_service` — action legality checking
- `land_service` — quadrant unlocking

### 7. Domain Model

`agent/domain/` contains pure data models with no side effects:

- `game_state.py` — root aggregate
- `farm.py` — player farm with tiles, quadrants, buildings, workers
- `tile.py` — grid tile (empty, plant, weed, coop, pasture)
- `crop.py` — crop lifecycle state
- `animal.py` — animal lifecycle state
- `worker.py` — farm worker (farmer or hired hand)
- `inventory.py` — item inventory with capacity
- `market.py` — market state
- `season.py` — turn/day tracking
- `quadrant.py` — land quadrant management
- `wallet.py` — money tracking
- `town.py` — town demand state
- `player.py` — player data
- `position.py` — grid position

### 8. Action Adapter

`agent/adapters/action_adapter.py` serializes the internal action dict into
the exact Kaggle format: `{"farmer": [...], "hands": [...], "market": [...]}`.
It validates and normalizes action lists before submission.

## Data Flow (Turn Lifecycle)

```
Observation Received → ObservationAdapter.parse(obs) → GameState
        ↓
DecisionContext constructed from GameState + Settings
        ↓
ActionGenerator generates candidate actions
        ↓
ActionFilter removes illegal candidates
        ↓
ActionValidator validates remaining candidates
        ↓
StrategyEngine.score_action() evaluates each candidate
        ↓
Ranker selects highest-scored candidate (deterministic tie-break)
        ↓
ActionAdapter.convert(action) → Kaggle action dict
        ↓
Action returned to Kaggle environment
```

## Dependencies

```
main.py
  ├── agent/agent.py (composition root)
  │     ├── agent.adapters (ObservationAdapter, ActionAdapter)
  │     ├── agent.decision (DecisionEngine, DecisionContext)
  │     ├── agent.strategies (StrategyEngine, BaselineStrategy)
  │     ├── agent.services (business logic)
  │     ├── agent.domain (pure models)
  │     ├── agent.config (Settings)
  │     ├── agent.exceptions (exception hierarchy)
  │     ├── agent.logging (structured logging)
  │     └── agent.observability (tracing, telemetry, metrics)
  └── kaggle_environments (official SDK)
```

## Architectural Principles

- **Domain isolation:** All game logic lives in `agent/domain/` with zero
  dependencies on infrastructure.
- **Adapter isolation:** Kaggle-specific integration is confined to
  `agent/adapters/`.
- **Immutability:** Domain objects are immutable value objects.
- **Deterministic fallback:** Any error path produces a safe `PASS` action.
- **Observability:** Every decision is traced, metered, and recorded.
