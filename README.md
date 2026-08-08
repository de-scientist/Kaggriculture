# Kaggriculture AI — Stage 1 Baseline

An autonomous AI agent for the Kaggriculture farming competition on Kaggle.

## Competition Objective

Kaggriculture is a two-player farming simulation. Each player manages a
farm over a 30-day season (720 turns) and competes to earn the most coins
by buying seeds and livestock, planting, watering, harvesting, raising
animals, hiring help, and trading on a dynamic market.

**Official Entry Point:** `main.py` with `agent(obs: dict) -> dict`

## Key Features

- **Observation Adapter** — Parses raw Kaggle observations into a typed
  domain model
- **Decision Engine** — Generates, filters, validates, and ranks actions
  deterministically
- **Baseline Strategy** — Rule-based priority system with weighted scoring
- **Core Services** — Crop, animal, worker, inventory, market, and land
  lifecycle management
- **Observability** — Structured logging, tracing, telemetry, and
  performance budgets
- **Safe Fallback** — Any error produces a `PASS` action to avoid crashing
  the episode

## Architecture Overview

```
Official Environment (Kaggle)
        ↓
Observation Adapter → GameState (domain)
        ↓
Decision Engine → Strategy Engine → Services → Domain
        ↓
Action Adapter → Official Environment (Kaggle)
```

See [Architecture Documentation](docs/architecture/) for details.

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Package manager | pip / uv (lockfile: `uv.lock`) |
| Build backend | hatchling |
| Testing | pytest |
| Linting | ruff |
| Formatting | black |
| Type checking | mypy (strict) |
| Kaggle integration | kaggle-environments |

## Repository Structure

```
kaggriculture-agent/
├── main.py                         # Official entry point
├── agent/
│   ├── __init__.py
│   ├── agent.py                    # Agent function (composition root)
│   ├── adapters/                   # Kaggle ↔ domain translation
│   ├── decision/                   # Decision engine
│   ├── domain/                     # Pure domain models
│   ├── services/                   # Business logic
│   ├── strategies/                 # Decision algorithms
│   ├── config/                     # Configuration
│   ├── exceptions/                 # Exception hierarchy
│   ├── logging/                    # Structured logging
│   ├── observability/              # Tracing, telemetry, metrics
│   └── utilities/                  # Helpers
├── tests/
│   ├── fixtures/                   # Shared test fixtures
│   ├── unit/                       # Unit tests
│   └── integration/                # Integration tests
├── configs/                        # YAML configuration files
├── scripts/                        # Utility scripts
├── docs/                           # Full documentation
├── reports/                        # Stage 1 reports
├── benchmarks/                     # Benchmark documentation
├── .github/workflows/              # CI/CD
├── submission_manifest.json        # Submission metadata
├── pyproject.toml
└── uv.lock
```

## Installation

```bash
# Install in development mode
pip install -e ".[dev]"

# Or with uv
uv sync
```

## Configuration

Default configuration is loaded from `configs/`. Override with environment
variables:

```bash
export KAG_ENV=development      # config profile
export KAG_AGENT_SEED=42        # random seed
export KAG_LOG_LEVEL=INFO       # log level
```

See [Configuration Documentation](docs/operations/configuration.md).

## Running Locally

```bash
# Run a game against a random opponent (requires kaggle-environments)
python -c "
from kaggle_environments import make
env = make('kaggriculture', debug=True)
env.run(['main.py', 'random'])
print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
"

# Run directly
python main.py
```

## Running Tests

```bash
# All tests (510 tests)
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=agent --cov-fail-under=80
```

## Running Benchmarks

```bash
python scripts/benchmark.py
```

## Submission Preparation

```bash
# Validate submission
python scripts/validate_submission.py

# Build submission package
tar -czf submission.tar.gz main.py agent/

# Submit to Kaggle
kaggle competitions submit kaggriculture -f submission.tar.gz -m "Stage 1 baseline v1.0.0"
```

See [Submission Guide](docs/competition/kaggriculture_submission.md) and
[Submission Checklist](docs/competition/submission_checklist.md).

## Current Strategy

The Stage 1 baseline strategy is a **deterministic, rule-based** approach
that prioritizes:

1. Emergency (sell if shed near capacity)
2. Survival (water crops about to die)
3. Harvest (collect mature crops)
4. Plant (plant available seeds)
5. Water (growth phase watering)
6. Fertilize (bonus window)
7. Animal care (feed, care, collect)
8. Market (buy seeds, buy land, hire)
9. Movement (navigate to targets)
10. Fallback (PASS)

See [Baseline Strategy](docs/strategy/baseline_strategy.md) and
[Decision Priorities](docs/strategy/decision_priorities.md).

## Performance Baseline

| Metric | Value | Budget |
|---|---|---|
| Average decision latency | 5.4 ms | 500 ms |
| P95 latency | 10.4 ms | 500 ms |
| P99 latency | 52.5 ms | 500 ms |

See [Performance Report](reports/stage_1_performance.md).

## Known Limitations

- No multi-turn planning (single-turn lookahead)
- No market price forecasting
- No opponent modeling
- No dynamic weight adjustment
- Full 720-turn Kaggle episode not validated in CI

See [Competition Notes](docs/competition/competition_notes.md) for the
full list.

## Stage 1 Status

**READY** — All acceptance criteria verified. See
[Stage 1 Completion Report](STAGE_1_COMPLETION_REPORT.md).

## License

See [LICENSE](LICENSE).
