# Deployment

## Primary Target

**Official Kaggle Competition Runtime**

The agent is deployed via `kaggle competitions submit kaggriculture`.
The submission package must contain `main.py` (with the `agent` function)
and the `agent/` package.

## No Additional Infrastructure

The following are **NOT** required or included:

- Web servers
- Databases
- REST APIs
- Frontend applications
- Cloud services
- External API calls

The competition agent is self-contained within the Kaggle runtime.

## Deployment Steps

1. **Validate** — Run `scripts/validate_submission.py`
2. **Test** — Run full test suite: `pytest`
3. **Lint** — Run `ruff check agent/ tests/`
4. **Format check** — Run `ruff format --check agent/ tests/`
5. **Type check** — Run `mypy agent/`
6. **Package** — Build tarball: `tar -czf submission.tar.gz main.py agent/`
7. **Submit** — `kaggle competitions submit kaggriculture -f submission.tar.gz -m "message"`
8. **Monitor** — Check `kaggle competitions episodes <SUBMISSION_ID>`

## CI/CD Deployment

GitHub Actions workflows are in `.github/workflows/`:

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | Push/PR | Quality gates (lint, typecheck, tests) |
| `coverage.yml` | Push/PR | Coverage reporting |
| `benchmarks.yml` | Schedule | Performance tracking |
| `submission.yml` | Manual | Build and validate submission package |

## Versioning

Each submission is tagged with the git commit hash:

```bash
git describe --tags --always
```

The `submission_manifest.json` records the version metadata.
