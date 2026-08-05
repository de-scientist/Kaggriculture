# API Reference

## agent.agent

The official Kaggle entry point.

```python
def agent(obs: dict) -> dict:
    """Receive observation, return action."""
```

## agent.adapters

### observation_adapter

```python
def adapt(obs: dict) -> GameState
```

### action_adapter

```python
def to_kaggle_format(action: InternalAction) -> dict
def validate(action: dict) -> bool
```

### serialization

```python
def serialize_game_state(state: GameState) -> dict
def deserialize_game_state(data: dict) -> GameState
```

## agent.decision

### decision_engine

```python
class DecisionEngine:
    def decide(self, context: DecisionContext) -> Action
```

### action_generator

```python
def generate_candidates(context: DecisionContext) -> list[Action]
```

### action_validator

```python
def validate(action: Action, context: DecisionContext) -> bool
```

### action_ranker

```python
def rank(candidates: list[Action], context: DecisionContext) -> list[Action]
```

### candidate_actions

```python
def build_candidates(context: DecisionContext) -> list[Action]
```

### decision_context

```python
@dataclass
class DecisionContext:
    obs: dict
    player: int
    game_state: GameState
    config: dict
```

## agent.strategies

### strategy

```python
class Strategy(ABC):
    def rank(self, candidates: list[Action], context: DecisionContext) -> list[Action]
```

### baseline_strategy

```python
class BaselineStrategy(Strategy): ...
```

### strategy_manager

```python
class StrategyManager:
    def get_strategy(self, name: str) -> Strategy
```

## agent.domain

All domain models are plain Python dataclasses with no external dependencies.

## agent.services

All services coordinate domain objects and contain no infrastructure code.

## agent.planning

Planners and schedulers are independent from strategy selection.

## agent.economy

Economic calculations are deterministic with no forecasting.

## agent.market

Market snapshot and analyzer track prices, demand, supply, and trends.

## agent.inventory

Inventory manager, capacity, and reservation modules.

## agent.crops

Crop tracker, growth, watering, harvesting, and fertilizer modules.

## agent.animals

Animal tracker, feeding, production, and health modules.

## agent.workers

Worker manager, scheduler, tasks, and movement modules.

## agent.utilities

Constants, helpers, logging, timers, math, and collections utilities.

## agent.exceptions

Centralized exception hierarchy with domain-specific error types.

## agent.config

Settings loader and validator for YAML configuration.