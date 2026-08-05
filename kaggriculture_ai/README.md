# Kaggriculture AI Platform - Stage 1

Production-ready baseline AI for the Kaggriculture Kaggle competition.

## Overview

This is the Stage 1 deterministic baseline agent that matches the behavior of the official `starter` agent while providing a modular, extensible architecture for future AI improvements.

## Architecture

The agent follows Clean Architecture with 7 layers:

1. **Kaggle Agent Boundary** - `main.py` submission surface
2. **Adapters** - Observation and action serialization
3. **Domain Model** - Pure business logic and game mechanics
4. **Decision Engine** - Orchestrates planners and strategies
5. **Strategy** - Scoring and selection policy
6. **Validator** - Mirrors engine preconditions
7. **Serializer** - Emits official action dict

## Usage

```python
from kaggriculture_ai.agent import agent

# The agent function is the Kaggle submission entry point
action = agent(observation)
```

## Development

```bash
# Install dependencies
pip install -e .

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

## Strategy Stages

- Stage 1: Deterministic baseline (current)
- Stage 2: Heuristic improvements
- Stage 3: Economic models
- Stage 4: Utility optimization
- Stage 5+: MCTS, RL, Hybrid AI