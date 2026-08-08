# Configuration

## Overview

Configuration is managed by `agent/config/` and loaded from YAML files in
`configs/`. The system supports environment-variable overrides and
feature flags.

## Configuration Files

| File | Purpose |
|---|---|
| `configs/development.yaml` | Development configuration |
| `configs/production.yaml` | Production (competition) configuration |
| `configs/test.yaml` | Test configuration |
| `configs/settings.yaml` | Default settings (loaded first) |

## Configuration Hierarchy

Override precedence (highest wins):

1. Environment variables (`KAG_AGENT_*`)
2. Runtime override (passed to `get_config()`)
3. Environment profile (`KAG_ENV`)
4. Default profile (`configs/default.yaml`)

## Settings

`agent/config/settings.py` defines the `Settings` dataclass:

| Field | Type | Default | Description |
|---|---|---|---|
| `seed` | `int` | 42 | Random seed for determinism |
| `strategy_name` | `str` | "baseline" | Strategy to use |
| `board_size` | `int` | 10 | Farm board size |
| `starting_money` | `float` | 3000.0 | Starting bank balance |
| `shed_capacity` | `int` | 100 | Shed item capacity |
| `turns_per_day` | `int` | 24 | Turns per in-game day |
| `total_days` | `int` | 30 | Days per season |
| `farm_hand_cost_mult` | `float` | 1.0 | Multiplier for hire cost |
| `weed_spawn_chance` | `float` | 0.005 | Per-tile weed spawn chance |
| `max_market_orders_per_turn` | `int` | 10 | Max market orders per turn |
| `observation_parsing_budget_ms` | `float` | 5.0 | Budget for observation parsing |
| `decision_engine_budget_ms` | `float` | 20.0 | Budget for decision engine |
| `strategy_evaluation_budget_ms` | `float` | 10.0 | Budget for strategy evaluation |
| `action_conversion_budget_ms` | `float` | 2.0 | Budget for action conversion |
| `total_decision_budget_ms` | `float` | 500.0 | Total per-turn budget |
| `logging_level` | `str` | "INFO" | Log level |
| `log_format` | `str` | "json" | Log format (json or standard) |
| `enable_tracing` | `bool` | True | Enable decision tracing |
| `enable_telemetry` | `bool` | True | Enable telemetry recording |
| `enable_metrics` | `bool` | True | Enable metrics recording |
| `enable_replay` | `bool` | True | Enable replay recording |

## Environment Variables

| Variable | Description |
|---|---|
| `KAG_ENV` | Environment profile (development, production, test) |
| `KAG_AGENT_SEED` | Override random seed |
| `KAG_AGENT_STRATEGY` | Override strategy name |
| `KAG_LOG_LEVEL` | Override logging level |
| `KAG_ENABLE_TRACING` | Enable/disable tracing (true/false) |

## Feature Flags

Feature flags are boolean settings that can be toggled without code changes:

| Flag | Default | Description |
|---|---|---|
| `enable_tracing` | true | Record decision traces |
| `enable_telemetry` | true | Record telemetry metrics |
| `enable_metrics` | true | Record performance metrics |
| `enable_replay` | true | Record replay data |
| `enable_market_analysis` | false | Enable market trend analysis (Stage 2) |
| `enable_planning` | false | Enable multi-turn planning (Stage 2) |

## Example Configuration

```yaml
# configs/development.yaml
agent:
  seed: 42
  strategy_name: "baseline"
  board_size: 10
  starting_money: 3000.0

farming:
  shed_capacity: 100
  turns_per_day: 24
  total_days: 30
  farm_hand_cost_mult: 1.0
  weed_spawn_chance: 0.005
  max_market_orders_per_turn: 10

performance:
  observation_parsing_ms: 5.0
  decision_engine_ms: 20.0
  strategy_evaluation_ms: 10.0
  action_conversion_ms: 2.0
  total_decision_ms: 500.0

observability:
  enable_tracing: true
  enable_telemetry: true
  enable_metrics: true
  enable_replay: true

logging:
  level: "INFO"
  format: "json"
```
