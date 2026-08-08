# Troubleshooting

## Import Errors

### `ModuleNotFoundError: No module named 'agent'`

**Cause:** The package is not installed or the working directory is wrong.

**Resolution:**

```bash
pip install -e .
# Or ensure you're in the project root
```

### `ImportError` in agent module

**Cause:** Missing dependency or circular import.

**Resolution:**

```bash
pip install -e ".[dev]"
python -c "from agent.agent import agent; print('OK')"
```

## Dependency Installation Failures

### `pip install -e .` fails

**Cause:** Build backend not installed or Python version too old.

**Resolution:**

```bash
python --version  # Must be 3.11+
pip install --upgrade pip
pip install -e ".[dev]"
```

## Configuration Errors

### `SettingsError: Configuration file not found`

**Cause:** No config file at the expected path.

**Resolution:**

```bash
ls configs/  # Should contain development.yaml, production.yaml
export KAG_ENV=development  # Or create config file
```

## Invalid Observations

### Agent returns PASS for valid observations

**Cause:** The observation doesn't match the expected schema.

**Diagnostic:**

```bash
python scripts/validate_submission.py
```

If the agent returns PASS, check:

1. `player` field is present and is an integer
2. `farms` has entries for both players
3. `farms[player]` has `money`, `tiles`, `farmer`
4. `private` has `shed`, `seeds`, `inventories`
5. `market` has `inventory`, `prices`
6. `town` has `unlocked_shops`

### `ObservationParseError`

**Cause:** A required field is missing or malformed.

**Diagnostic:** Check the error message for the specific field.

## Invalid Actions

### `ValueError` in ActionAdapter

**Cause:** The action dict doesn't match the expected schema.

**Diagnostic:** The error message indicates which key is missing.

**Resolution:** Ensure the action dict has `farmer`, `hands`, and `market`
keys. The `farmer` key is optional (defaults to `["PASS"]`).

## Strategy Failures

### Agent always returns PASS

**Cause:** All candidate actions were filtered out.

**Diagnostic:** Enable debug logging:

```bash
export KAG_LOG_LEVEL=DEBUG
python -c "from kaggle_environments import make; env = make('kaggriculture', debug=True); env.run(['main.py', 'random'])"
```

### Non-deterministic behavior

**Cause:** Random seed not set or not passed correctly.

**Resolution:**

```bash
export KAG_AGENT_SEED=42  # Fixed seed
```

## Performance Problems

### Decision latency > 500 ms

**Cause:** Observation parsing or strategy evaluation is slow.

**Diagnostic:**

```bash
python benchmarks/benchmark.py
```

**Resolution:** Check telemetry for which component exceeds the budget.

### Memory growth over many decisions

**Cause:** Telemetry or tracing accumulating data without reset.

**Resolution:** Call `telemetry.reset_step()` or `telemetry.clear_history()`
between episodes.

## Submission Validation Failures

### `scripts/validate_submission.py` fails

**Diagnostic:** Read the failure output for specific check that failed.

Common issues:
- `main.py` not found — ensure it's at repo root
- Agent not importable — check imports
- Agent exceptions on minimal observation — check error handling

## Still Stuck?

1. Run `./scripts/validate_submission.py` for a full diagnostic report
2. Check `logs/` for recent log entries
3. Review telemetry reports for failure patterns
4. Open an issue with the error message, traceback, and observation data
