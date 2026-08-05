# Architecture

## Overview

The Kaggriculture AI platform is organized as a modular Python package with strict separation of concerns. Every package satisfies the four principles: Single Responsibility, Explicit Interfaces, High Cohesion, and Low Coupling.

## Package Dependency Graph

```
agent.py (entry point)
  └── agent/adapters/        (Kaggle ↔ domain translation)
  └── agent/decision/        (core reasoning engine)
  │     └── agent/strategies/ (decision algorithms)
  └── agent/domain/          (pure domain models, no external deps)
  └── agent/services/        (business logic, coordinates domain objects)
  └── agent/planning/        (task scheduling)
  └── agent/economy/         (economic calculations)
  └── agent/market/          (market state tracking)
  └── agent/inventory/       (inventory management)
  └── agent/crops/           (crop lifecycle)
  └── agent/animals/         (animal lifecycle)
  └── agent/workers/         (worker management)
  └── agent/utilities/       (reusable utilities)
  └── agent/exceptions/      (exception hierarchy)
  └── agent/config/          (application settings)
```

## Key Design Decisions

1. **No Kaggle API dependencies in domain or services.** Business logic is fully isolated from infrastructure.
2. **Adapters are the only boundary** between Kaggle objects and internal domain objects.
3. **Strategies implement a common interface**, enabling hot-swapping of algorithms.
4. **Configuration is centralized** in `configs/` and never hard-coded.
5. **Logging is centralized** via the `utilities/logging` module.

## Extension Points

- Add new strategies by implementing the strategy interface in `agent/strategies/`.
- Add new services by creating a module in `agent/services/`.
- Add new domain models by extending `agent/domain/`.
- Add new adapters by extending `agent/adapters/`.