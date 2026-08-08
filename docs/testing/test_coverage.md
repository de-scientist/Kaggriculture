# Test Coverage

## Current Coverage Targets

| Layer | Target | Current |
|---|---|---|
| Domain | 90% | Measured via `pytest --cov=agent/domain` |
| Adapters | 80% | Measured via `pytest --cov=agent/adapters` |
| Decision Engine | 85% | Measured via `pytest --cov=agent/decision` |
| Services | 85% | Measured via `pytest --cov=agent/services` |
| Strategies | 80% | Measured via `pytest --cov=agent/strategies` |
| Overall | 80% | Enforced via `--cov-fail-under=80` |

## Coverage Configuration

Defined in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["agent"]
omit = ["tests/*", "agent/config/*"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80
```

## How to Check Coverage

```bash
# Full report with missing lines
pytest --cov=agent --cov-report=term-missing

# Per-module report
pytest --cov=agent/domain --cov=agent/decision --cov-report=term-missing

# HTML interactive report
pytest --cov=agent --cov-report=html
# Then open: htmlcov/index.html
```

## Coverage Exclusions

The following are excluded from coverage:

- `pragma: no cover` — explicit exclusions
- `raise NotImplementedError` — abstract methods
- `if __name__ == .__main__.:` — entry points
- `agent/config/*` — configuration loading (tested separately)

## Improving Coverage

To add test coverage:

1. Identify uncovered lines from the `--cov-report=term-missing` output.
2. Add unit tests for the uncovered code paths.
3. Add integration tests for cross-component interactions.
4. Verify coverage increases with `--cov-report=term`.
