# Packaging

## Overview

The project is packaged using `hatchling` as the build backend,
configured in `pyproject.toml`.

## Build Commands

```bash
# Build source distribution
python -m build --sdist

# Build wheel
python -m build --wheel

# Build all
python -m build
```

## Package Structure

```
kaggriculture_agent/
├── main.py              # Entry point (required by Kaggle)
├── agent/               # Production code package
│   ├── __init__.py
│   ├── agent.py         # Agent function (composition root)
│   ├── adapters/
│   ├── decision/
│   ├── domain/
│   ├── services/
│   ├── strategies/
│   ├── config/
│   ├── exceptions/
│   ├── logging/
│   └── observability/
├── configs/             # YAML configuration files
├── tests/
├── scripts/
├── docs/
├── benchmarks/
├── pyproject.toml
├── uv.lock
└── README.md
```

## Submission Package

The Kaggle competition requires `main.py` at the root with an `agent`
function. For multi-file submissions:

```bash
tar -czf submission.tar.gz main.py agent/
kaggle competitions submit kaggriculture -f submission.tar.gz -m "v1.0.0"
```

## Dependency Exclusion

Development-only dependencies (`ruff`, `mypy`, `pytest`, `mkdocs`) are
listed under `[project.optional-dependencies] dev` and are excluded from
the competition runtime. The competition environment provides
`kaggle-environments` and `pyyaml`.

## Validation

Before building the submission package:

```bash
python scripts/validate_submission.py
```

This checks:

- Required files exist (`main.py`, `agent/__init__.py`, `agent/agent.py`)
- All imports resolve
- Agent executes on a minimal observation
- Malformed observation falls back to PASS safely
