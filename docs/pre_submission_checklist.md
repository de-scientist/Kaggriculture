# Pre-Submission Checklist

## Code Quality

- [ ] Working tree clean (`git status` shows no uncommitted changes)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Lint passes (`ruff check agent/ tests/ scripts/`)
- [ ] Type checking passes (`mypy agent/ tests/`)
- [ ] Formatting passes (`ruff format --check agent/ tests/ scripts/`)
- [ ] Coverage threshold passes (`pytest --cov=agent --cov-fail-under=80`)

## Agent

- [ ] Entry point works (`python main.py` imports successfully)
- [ ] Observation adapter parses valid observations
- [ ] Observation adapter fails predictably on malformed input
- [ ] Action adapter converts valid domain actions
- [ ] Action adapter rejects invalid actions
- [ ] Decision engine returns valid action dicts
- [ ] Decision engine falls back to PASS on errors
- [ ] Baseline strategy produces deterministic output

## Simulation

- [ ] Full 720-turn episode completes without crashes
- [ ] No illegal actions produced
- [ ] No fatal exceptions during episode
- [ ] Final state is valid
- [ ] Agent handles malformed observations gracefully

## Performance

- [ ] Average decision latency < 50 ms
- [ ] P95 decision latency < 200 ms
- [ ] P99 decision latency < 500 ms
- [ ] Memory usage acceptable (no leaks over 500 decisions)
- [ ] No obvious performance regressions vs. baseline

## Submission

- [ ] `scripts/validate_submission.py` passes all checks
- [ ] Required files included (`main.py`, `agent/` package)
- [ ] Required dependencies available (`kaggle-environments`, `pyyaml`)
- [ ] Agent function exported from `main.py`
- [ ] Package builds successfully (`python -m build`)

## Determinism

- [ ] Identical observations produce identical actions
- [ ] Full episode is reproducible across runs

## Observability

- [ ] Decision count metric recorded on every decision
- [ ] Decision count metric recorded on fallback path
- [ ] Exceptions recorded in telemetry
- [ ] Performance budgets enforced
