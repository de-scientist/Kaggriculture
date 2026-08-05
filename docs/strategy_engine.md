# Strategy Engine

## Purpose

The strategy engine encapsulates decision-making algorithms. Every strategy implements a common interface, enabling hot-swapping and comparison.

## Public Interface

### `Strategy`

```python
class Strategy(ABC):
    def rank(self, candidates: list[Action], context: DecisionContext) -> list[Action]: ...
```

## Built-in Strategies

### `BaselineStrategy`

A deterministic baseline that prioritizes:
1. Harvesting mature crops
2. Watering crops in the bonus window
3. Planting available seeds
4. Selling produce at market
5. Buying seeds when supply is low
6. Passing

## Future Strategies

- `HeuristicStrategy` — rule-based with tunable weights
- `MCTSStrategy` — Monte Carlo tree search
- `BeamSearchStrategy` — beam search over action sequences
- `RLStrategy` — reinforcement learning agent
- `HybridStrategy` — combines multiple strategies

## Extension Points

- Implement the `Strategy` ABC to add a new algorithm.
- Register new strategies in `StrategyManager`.
- Configure the active strategy via `configs/strategy.yaml`.