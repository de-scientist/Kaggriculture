# Logging

## Overview

The agent uses structured logging via `agent/logging/`. All log entries
are emitted as JSON (in production) or human-readable text (in
development) with consistent fields.

## Log Fields

Every log entry includes:

| Field | Description |
|---|---|
| `timestamp` | ISO 8601 timestamp |
| `severity` | INFO, WARNING, ERROR, DEBUG |
| `component` | Emitting module/component |
| `action` | Action being performed |
| `message` | Human-readable description |
| `turn` | Current game turn (if available) |
| `day` | Current game day (if available) |
| `player` | Player index (if available) |
| `strategy` | Strategy name (if available) |
| `correlation_id` | Trace correlation ID |
| `execution_time_ms` | Per-component timing |
| `decision_id` | Unique decision identifier |

## Log Levels

| Level | Usage |
|---|---|
| DEBUG | Detailed diagnostic information |
| INFO | Normal operational messages (parsing, decisions) |
| WARNING | Unexpected but recoverable conditions |
| ERROR | Errors that were caught and handled |

## Logger Access

```python
from agent.logging import get_logger

logger = get_logger("agent.decision")
logger.info("Decision made", turn=120, action="PLANT_WHEAT")
logger.error("Processing error", exc_info=True, component="DecisionEngine")
```

## Performance Logging

The `logger.performance()` method records timing:

```python
logger.performance("DecisionEngine", elapsed_ms, turn=step, day=day)
```

This automatically logs at INFO level if within budget, WARNING if
exceeding the target threshold.
