# Coding Standards

## Python Style

- **Line length:** 100 characters (enforced by ruff/black)
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Alphabetical, grouped (stdlib, third-party, local)
- **Type hints:** Required on all public functions and methods
- **Docstrings:** Required on all public modules, classes, and functions

## Naming Conventions

| Convention | Example |
|---|---|
| Classes | `PascalCase` — `CropService` |
| Functions/methods | `snake_case` — `harvest_crop` |
| Variables | `snake_case` — `crop_age` |
| Constants | `UPPER_SNAKE` — `MAX_BOARD_SIZE` |
| Private members | `_snake_case` — `_internal_cache` |

## Type Checking (mypy)

Use strict type checking:

```bash
mypy agent/ --strict
```

- All public functions must have full type annotations
- `Optional` and `Union` types must be explicit
- `Any` should be avoided; use `object` or generics where possible
- `# type: ignore` must include a reason: `# type: ignore[attr-defined]`

## Immutability

Domain model objects should be immutable:

- Use `__slots__` to prevent attribute addition
- Methods that change state return a new instance
- Properties are read-only

## Error Handling

- Raise specific exceptions from `agent.exceptions`
- Never catch and silently swallow exceptions
- Always log errors with context
- Use `try/except` at the agent boundary, not in domain logic

## Logging

- Use `get_logger(__name__)` to create loggers
- Log at INFO for normal operations
- Log at WARNING for unexpected but recoverable conditions
- Log at ERROR for failures
- Include context (turn, day, player) in log messages

## Testing

- Place test files in `tests/unit/` mirroring the source structure
- Name test files `test_<module>.py`
- Name test classes `Test<Module>`
- Name test methods `test_<behavior>`
- Use `@pytest.mark.parametrize` for data-driven tests
- Use `@pytest.mark.regression` for regression tests
- Use `@pytest.mark.determinism` for determinism tests

## Documentation

- Every public module, class, and function must have a docstring
- Docstrings should include Args, Returns, and Raises sections
- Keep documentation in sync with code changes
