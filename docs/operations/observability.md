# Observability

## Overview

The observability layer (`agent/observability/`) provides structured
tracing, telemetry, metrics, and performance budget enforcement.

## Components

| Component | Module | Purpose |
|---|---|---|
| `Tracer` | `agent/observability/tracing.py` | Decision tracing with correlation IDs |
| `Telemetry` | `agent/observability/telemetry.py` | Record decisions, exceptions, fallback events |
| `PerformanceBudget` | `agent/observability/performance.py` | Enforce timing budgets per component |
| `DecisionTrace` | `agent/observability/tracing.py` | Individual trace record |

## Tracer

Generates correlation IDs for each decision and records trace entries:

```python
tracer = get_default_tracer()
tracer.set_correlation_id(make_correlation_id(seed, player))
tracer.start_trace("decision", turn=step)
# ... decision work ...
tracer.end_trace("decision", result="PLANT")
```

## Telemetry

Records:

- Decision count (every decision, including fallbacks)
- Exception count (by exception type)
- Fallback count (PASS fallback triggered)
- Performance samples per component

```python
telemetry = get_telemetry()
telemetry.record_decision()
telemetry.record_exception("ValueError")
telemetry.record_fallback()
```

## Performance Budgets

Default budgets (milliseconds):

| Component | Target | Critical |
|---|---|---|
| Observation parsing | 5 ms | 50 ms |
| Decision engine | 20 ms | 100 ms |
| Strategy evaluation | 10 ms | 50 ms |
| Action conversion | 2 ms | 10 ms |
| Total decision | 500 ms | 1500 ms |

Status classification:

- **OK** — within target
- **WARNING** — exceeded target but below failure threshold
- **CRITICAL** — exceeded failure threshold

## Metrics Access

```python
from agent.observability import get_telemetry, get_default_tracer

telemetry = get_telemetry()
report = telemetry.report()
# {'decisions': 120, 'exceptions': 0, 'fallbacks': 3}
```
