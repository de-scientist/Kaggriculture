# Replay Testing

## Overview

Replay testing verifies that the agent produces valid actions in a full
Kaggle environment episode. The agent is run against simulated or
recorded observations to ensure end-to-end correctness.

## How Replay Works

1. The `scripts/validate_submission.py` script generates a minimal valid
   observation.
2. The agent processes it and returns an action.
3. The action is validated against the Kaggle action schema.
4. If Kaggle environments is installed, a full 720-turn episode is simulated.

## Test Scenarios

| Scenario | Description |
|---|---|
| Minimal observation | Starting game state (day 0, all tiles empty) |
| With crop | A wheat plant on the board |
| With animal | A goose in a coop |
| With market prices | Custom market prices set |
| With hands | Hired farm hands present |
| With money | Custom bank balance |
| Malformed observation | Missing required fields → fallback to PASS |
| Advanced observation | Mid-game state (day 5, multiple quadrants) |

## Validation Checks

For each scenario, the validator checks:

1. Agent returns a valid dict (not None, not an exception)
2. Action has keys: `farmer`, `hands`, `market`
3. `farmer` is a non-empty list with a valid action
4. `hands` is a list (may be empty)
5. `market` is a list (may be empty)
6. No invalid actions are submitted

## Running Replay Tests

```bash
python scripts/validate_submission.py
```

Expected output:

```
=== Submission Validation Report ===

  [PASS] File exists: main.py
  [PASS] File exists: agent/__init__.py
  [PASS] File exists: agent/agent.py
  [PASS] Agent importable
  [PASS] Adapters importable
  [PASS] Decision engine importable
  [PASS] Dependency available: kaggle_environments
  [PASS] Agent executes on observation
  [PASS] Action is dict
  [PASS] Action has required keys
  [PASS] Farmer action is non-empty list
  [PASS] Malformed observation falls back to PASS

12 passed, 0 failed, 0 skipped
```
