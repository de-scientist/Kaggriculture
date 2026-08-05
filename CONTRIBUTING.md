# Contributing

## Coding Standards

- Follow PEP 8 and the project's ruff/black configuration.
- Use type hints on all public functions and methods.
- Keep functions under 50 lines; classes under 200 lines.
- Write docstrings for all public modules, classes, and functions.
- Use meaningful variable and function names; avoid abbreviations.

## Git Workflow

1. Create a feature branch from `main`: `git checkout -b feat/<description>`
2. Make your changes with clear, atomic commits.
3. Run the linter and tests before committing: `make lint && make test`
4. Push your branch and open a Pull Request against `main`.

## Pull Request Process

1. Ensure all checks pass (CI pipeline).
2. Provide a clear description of the change and its motivation.
3. Link any related issues.
4. At least one reviewer must approve before merging.

## Branch Strategy

- `main` — stable, release-ready code.
- `develop` — integration branch for ongoing work.
- `feat/*` — feature branches.
- `fix/*` — bugfix branches.
- `refactor/*` — refactoring branches.

## Code Review Requirements

- All production code changes require at least one reviewer.
- New modules must include corresponding tests.
- New public interfaces must be documented in `docs/`.

## Testing Expectations

- Unit tests must cover all new business logic.
- Integration tests must cover cross-module interactions.
- Performance benchmarks must be updated when decision latency changes.
- All tests must pass before a PR is merged.