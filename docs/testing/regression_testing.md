# Regression Testing

## Overview

Regression tests prevent previously discovered bugs from reappearing.
They are located in `tests/unit/` and tagged with the `regression` marker
where applicable.

## What Is Tested

| Bug | Regression Test | Description |
|---|---|---|
| `with_crop` raising on occupied tile | `test_with_crop_replaces_existing` | Verify tiles can be replanted |
| `Animal.produce()` not setting fertilizer | `test_can_collect_fertilizer_after_production` | Fertilizer available after production |
| `Season.remaining_turns` ignoring day | `test_remaining_turns_at_end` | Correct turn count at day 29 |
| `GameState` not deriving season from step | `test_advance_turn_at_day_boundary` | Day advances at step boundary |
| Scoring cost penalty sign error | `test_score_cost_penalty` | Expensive actions score lower |
| ActionAdapter empty market ops | `test_convert_empty_market_op_skipped` | Empty ops filtered from output |
| PerformanceBudget critical threshold | `test_performance_budget_critical` | Critical status triggers on failure threshold |
| Malformed observation fallback | `test_malformed_observation_falls_back_to_pass` | Invalid obs → PASS action |
| Decision engine fallback | `test_decide_fallback_returns_pass` | Error → PASS without crash |

## Running Regression Tests

```bash
pytest -m regression
```

## Adding New Regression Tests

When a bug is fixed:

1. Create a test that reproduces the bug (it should fail before the fix).
2. Apply the fix.
3. Verify the test passes.
4. Tag with `@pytest.mark.regression`.
5. Add an entry to this document.
