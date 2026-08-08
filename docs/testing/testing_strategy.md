# Testing Strategy

## Overview

The test suite is organized into:

- **Unit tests** (`tests/unit/`) — Test individual components in isolation
- **Integration tests** (`tests/integration/`) — Test multiple components together
- **Performance tests** (`tests/unit/test_determinism.py`, `tests/performance/`) — Deterministic and benchmark validation
- **Regression tests** (`tests/unit/test_*.py`) — Prevent known bugs from reappearing
- **Replay tests** (via `scripts/validate_submission.py`) — Simulate full episodes

## Test Framework

- **Framework:** pytest
- **Configuration:** `pyproject.toml` `[tool.pytest.ini_options]`
- **Import mode:** `importlib` (avoids package import side effects)
- **Coverage:** `pytest-cov` with 80% coverage threshold

## Test Markers

| Marker | Description |
|---|---|
| `unit` | Unit tests |
| `integration` | Integration tests |
| `performance` | Performance benchmarks |
| `e2e` | End-to-end tests |
| `regression` | Regression tests |
| `observability` | Observability layer tests |
| `determinism` | Determinism and reproducibility tests |

## Running Tests

```bash
# All tests
pytest

# Unit only
pytest -m unit

# With coverage
pytest --cov=agent --cov-fail-under=80

# Specific category
pytest tests/unit/
pytest tests/integration/
```

## Test Coverage Target

- **Overall:** ≥ 80%
- **Domain layer:** ≥ 90%
- **Decision engine:** ≥ 85%
- **Adapters:** ≥ 80%
- **Services:** ≥ 85%

## Coverage Reporting

```bash
# Terminal report
pytest --cov=agent --cov-report=term-missing

# HTML report
pytest --cov=agent --cov-report=html
```
