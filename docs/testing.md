# Testing

## Overview

The test suite is organized into four tiers:

| Directory | Purpose |
|---|---|
| `tests/unit/` | Unit tests for individual modules |
| `tests/integration/` | Integration tests for cross-module interactions |
| `tests/performance/` | Performance benchmarks and latency tests |
| `tests/replays/` | Replay-based regression tests |
| `tests/fixtures/` | Shared test fixtures and mock data |

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests only
pytest tests/integration/ -v

# Run with coverage
pytest --cov=agent --cov-report=html
```

## Test Expectations

- Every production module must have corresponding tests.
- Unit tests must cover all public interfaces.
- Integration tests must cover cross-module interactions.
- Performance tests must track decision latency.
- All tests must pass before a PR is merged.

## Test Patterns

- Use fixtures from `tests/fixtures/` for shared mock data.
- Mock Kaggle infrastructure in unit tests.
- Use real observation data in integration tests.
- Profile decision latency in performance tests.