# Action Adapter

## Purpose

The action adapter converts internal domain actions into the Kaggle-compatible action dict format. It validates the action schema before submission.

## Responsibilities

- Convert internal action objects to Kaggle action dicts
- Validate action schema (farmer ops, hand ops, market ops)
- Ensure actions are within Kaggle constraints
- Serialize actions for submission

## Public Interfaces

### `ActionAdapter`

```python
class ActionAdapter:
    def to_kaggle_format(self, action: InternalAction) -> dict: ...
    def validate(self, action: dict) -> bool: ...
```

## Extension Points

- Add new action type conversions as the game adds features.
- Extend validation rules for new action types.
- Add action serialization formats (JSON, binary, etc.).