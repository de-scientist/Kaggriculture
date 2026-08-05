# Decision Engine

## Purpose

The decision engine is the core reasoning module that transforms observations into actions. It generates candidate actions, validates legality, evaluates candidates, ranks them, and returns the best action.

## Responsibilities

- Generate candidate actions from the current game state
- Validate each candidate for legality
- Evaluate candidates using the active strategy
- Rank candidates by score
- Return the highest-ranked action

## Public Interfaces

### `DecisionEngine`

```python
class DecisionEngine:
    def decide(self, context: DecisionContext) -> Action: ...
```

### `DecisionContext`

Encapsulates all information needed for a decision: observation, private state, market, town, and configuration.

### `ActionGenerator`

Generates a list of candidate actions given the current context.

### `ActionValidator`

Validates that a candidate action is legal in the current state.

### `ActionRanker`

Scores and ranks candidate actions using the active strategy.

## Extension Points

- Replace the strategy used by `ActionRanker` to change decision-making behavior.
- Add new action types by extending `ActionGenerator` and `ActionValidator`.
- Plug in different ranking algorithms (heuristic, MCTS, RL) via the strategy interface.