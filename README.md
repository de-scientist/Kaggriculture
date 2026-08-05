# Kaggriculture AI

A long-term AI platform for the Kaggriculture farming competition. Built as a modular, extensible foundation for all future stages of the Kaggriculture AI project.

## Competition Overview

Kaggriculture is a two-player farming sim where each player manages a farm, competing to earn the most coins over a fixed season. Players buy seeds and livestock, plant, water, harvest, raise animals, hire help, and trade on a dynamic market.

## Architecture Summary

The agent is organized into the following packages:

| Package | Responsibility |
|---|---|
| `adapters/` | Translate between Kaggle objects and internal domain objects |
| `decision/` | Core reasoning engine — generate, validate, evaluate, and rank actions |
| `strategies/` | Decision-making algorithms (baseline, heuristic, MCTS, RL, etc.) |
| `domain/` | Pure domain models — game state, farm, tile, crop, animal, market, etc. |
| `services/` | Business logic — crop, animal, worker, inventory, market services |
| `planning/` | Task scheduling and priority management |
| `economy/` | Economic calculations — ROI, pricing, investment |
| `market/` | Market state tracking — snapshots, analysis, trends |
| `inventory/` | Inventory management — capacity, reservations |
| `crops/` | Crop lifecycle — growth, watering, harvesting, fertilizer |
| `animals/` | Animal lifecycle — feeding, production, health |
| `workers/` | Worker management — scheduling, movement, tasks |
| `utilities/` | Reusable utilities — constants, helpers, logging, math |
| `exceptions/` | Centralized exception hierarchy |
| `config/` | Application settings — loading and validation |

## Installation

```bash
pip install -e .
```

Or with uv:

```bash
uv sync
```

## Running Locally

```bash
# Run the agent locally against the Kaggle environment
python -m agent.agent

# Run tests
pytest

# Run with coverage
pytest --cov=agent

# Lint
ruff check agent/ tests/

# Format
black agent/ tests/
```

## Repository Structure

```
project/
├── configs/          # Centralized configuration (YAML)
├── docs/             # Developer documentation
├── agent/            # Production code package
│   ├── adapters/     # Kaggle ↔ domain translation
│   ├── decision/     # Core reasoning engine
│   ├── strategies/   # Decision algorithms
│   ├── domain/       # Domain models
│   ├── services/     # Business logic
│   ├── planning/     # Task scheduling
│   ├── economy/      # Economic calculations
│   ├── market/       # Market state
│   ├── inventory/    # Inventory management
│   ├── crops/        # Crop lifecycle
│   ├── animals/      # Animal lifecycle
│   ├── workers/      # Worker management
│   ├── utilities/    # Reusable utilities
│   ├── exceptions/   # Exception hierarchy
│   └── config/       # Application settings
├── tests/            # Test suite
├── scripts/          # Utility scripts
├── benchmarks/       # Performance benchmarks
├── experiments/      # Experiment results
├── logs/             # Application logs
└── .github/          # CI/CD workflows
```

## Development Workflow

1. Create a feature branch from `main`.
2. Implement the change with tests.
3. Run `ruff check` and `black --check` to ensure formatting.
4. Run `pytest` to verify all tests pass.
5. Open a Pull Request for review.

## Contribution Guide

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, git workflow, and testing expectations.