# Contributing

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Install dependencies: `pip install -e ".[dev]"`
4. Make changes with tests
5. Run quality gates: `./scripts/lint.py && ./scripts/test.py`
6. Open a Pull Request

## Branch Strategy

- `main` — Stable, deployable code (Stage 1 baseline)
- `feature/*` — New features (Stage 2+)
- `fix/*` — Bug fixes
- `docs/*` — Documentation changes

## Code Standards

- **Formatting:** `black agent/ tests/` (line length 100)
- **Linting:** `ruff check agent/ tests/`
- **Type checking:** `mypy agent/` (strict mode)
- **Tests:** All new code must have ≥ 80% unit test coverage

## Commit Messages

Follow conventional commits:

```
feat: add crop growth calculation
fix: handle None tile in observation adapter
docs: update baseline strategy documentation
test: add wheat lifecycle regression test
perf: optimize tile parsing
refactor: extract crop service from decision engine
```

## Testing

All tests must pass before merging:

```bash
pytest --cov=agent --cov-fail-under=80
```

Write tests for:

- New functionality
- Bug fixes (regression tests)
- Edge cases
- Error handling

## Documentation

Update documentation when functionality changes:

- Code changes → Update relevant `docs/` file
- New strategy → Update `docs/strategy/`
- New config → Update `docs/operations/configuration.md`
- New API → Update `docs/development/api.md`

## Pull Request Process

1. Ensure all quality gates pass
2. Update documentation
3. Add tests for new functionality
4. Reference any related issues
5. Assign reviewers
