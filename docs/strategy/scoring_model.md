# Scoring Model

## Overview

The scoring model (`agent/strategies/scoring.py`) evaluates each
candidate action using a weighted sum of eight factors. All weights are
defined as constants in the `WEIGHTS` dictionary.

## Weights

```python
WEIGHTS = {
    "profit": 1.0,
    "worker_efficiency": 0.3,
    "time_efficiency": 0.2,
    "inventory_impact": 0.15,
    "market_opportunity": 0.25,
    "resource_sustainability": 0.1,
    "action_cost": -0.5,
    "opportunity_cost": -0.2,
}
```

## Scoring Functions

### compute_profit_score

```python
return max(0.0, action.estimated_reward)
```

Returns the positive portion of estimated reward. Negative rewards (net
cost) contribute 0 to profit but are penalized via `action_cost_penalty`.

### compute_worker_efficiency_score

```python
return 1.0 if action.worker else 0.5
```

Full points if a worker is assigned, half otherwise.

### compute_time_efficiency_score

Rates actions by urgency:
- `harvest`, `sell`, `feed` → 1.0 (time-critical)
- `plant`, `water` → 0.7 (moderately urgent)
- All others → 0.3

### compute_inventory_impact_score

```python
return 0.5 if action.estimated_reward > 0 else 0.0
```

Actions that produce items get a bonus (selling clears shed space).

### compute_market_opportunity_score

```python
return 1.0 if action_type in ("sell", "buy_product") else 0.2
```

Market-timing actions get full points; others get a base value.

### compute_resource_sustainability_score

```python
return 1.0 if action.estimated_cost <= 0 else 0.5
```

Free actions get full sustainability; paid actions get partial credit.

### compute_action_cost_penalty

```python
return action.estimated_cost * WEIGHTS["action_cost"]
```

Negative penalty proportional to cost. Higher cost = more negative.

### compute_opportunity_cost_penalty

```python
return -abs(action.estimated_reward - action.estimated_cost) * WEIGHTS["opportunity_cost"]
```

Negative penalty for the spread between reward and cost.

## Final Score

```
total = Σ(factor * weight)
```

The total is a single float. Higher is better. Ties are broken
deterministically by the `Ranker`.
