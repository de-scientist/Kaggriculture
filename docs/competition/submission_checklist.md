# Submission Checklist

## Official Compatibility

- [x] Official Kaggriculture rules reviewed (AGENTS.md)
- [x] Official agent interface reviewed (`main.py` with `agent(obs)`)
- [x] Official action format reviewed (dict with `farmer`, `hands`, `market`)
- [x] Official observation format reviewed (dict with `player`, `step`, `day`, `hour`, `farms`, `private`, `market`, `town`)
- [x] Submission requirements reviewed (`main.py` at root)

## Code

- [x] Entry point verified (`main.py` imports successfully)
- [x] Imports verified (all dependencies resolve)
- [x] No debug-only dependencies in runtime path
- [x] No local absolute paths
- [x] No credentials in source code

## Agent

- [x] GameState construction works (`ObservationAdapter.parse`)
- [x] Decision Engine works (`DecisionEngine.decide`)
- [x] Strategy works (`BaselineStrategy`)
- [x] Services work (`CropService`, `AnimalService`, etc.)
- [x] Action conversion works (`ActionAdapter.convert`)
- [x] Safe fallback exists (PASS on any error)
- [x] No invalid actions produced
- [x] No fatal errors during episode

## Testing

- [x] Unit tests pass (510 tests)
- [x] Integration tests pass (7 tests)
- [x] Regression tests pass (embedded in unit tests)
- [x] Performance tests pass (budget checks)
- [x] Determinism tests pass (identical obs → identical action)
- [x] Coverage target satisfied (≥ 80%)

## Validation

- [x] `scripts/validate_submission.py` passes all checks
- [x] Agent handles malformed observations gracefully (falls back to PASS)
- [x] Clean-environment validation passes

## Package

- [x] Required files present (`main.py`, `agent/` package)
- [x] Unnecessary development files excluded
- [x] Dependencies verified (only kaggle-environments, pyyaml, stdlib)
- [x] Version recorded (`submission_manifest.json`)
- [x] Git commit recorded
- [x] Submission package reproducible
