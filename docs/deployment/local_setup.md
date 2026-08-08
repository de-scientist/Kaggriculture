# Local Setup

## Prerequisites

- **Python:** 3.11+ (tested on 3.13.14)
- **Package manager:** `pip` or `uv`
- **Kaggle CLI:** Required for submission (optional for local testing)

## Installation

### Option 1: pip

```bash
# Clone the repository
git clone <repo-url>
cd kaggriculture-agent

# Install in development mode
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"
```

### Option 2: uv

```bash
git clone <repo-url>
cd kaggriculture-agent

# Install dependencies and create venv
uv sync
```

## Kaggle Environments

```bash
pip install -U kaggle-environments
```

## Configuration

Default configuration is loaded from `configs/`. Override with:

```bash
# Environment variable
export KAG_ENV=development

# Or runtime override
export KAG_AGENT_SEED=123
export KAG_LOG_LEVEL=DEBUG
```

## Running the Agent Locally

```bash
# Run a single game against random opponent
python -c "
from kaggle_environments import make
env = make('kaggriculture', debug=True)
env.run(['main.py', 'random'])
print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
"
```

## Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=agent --cov-report=term-missing

# Specific test file
pytest tests/unit/domain/test_crop.py -v
```

## Running Benchmarks

```bash
python benchmarks/benchmark.py
```

## Running Validation

```bash
python scripts/validate_submission.py
```

## Troubleshooting

If you encounter import errors:

```bash
# Reinstall in editable mode
pip install -e . --force-reinstall --no-deps
```

If Kaggle environment is not found:

```bash
pip install -U kaggle-environments
```
