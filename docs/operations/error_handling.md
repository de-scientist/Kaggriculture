# Error Handling

## Exception Hierarchy

The agent uses a structured exception hierarchy defined in
`agent/exceptions/`.

```
agent.exceptions.AgentError (base)
├── ObservationParseError
├── DecisionError
│   ├── InvalidActionError
│   └── NoValidActionError
├── StrategyError
├── ValidationError
├── ServiceError
│   ├── CropServiceError
│   ├── AnimalServiceError
│   ├── MarketServiceError
│   └── InventoryServiceError
└── ConfigError
```

## Error Handling Strategy

### At the Agent Boundary (`agent/agent.py`)

The `agent()` function wraps the entire decision pipeline in a try/except.
Any exception results in:

1. Logging the error with context
2. Recording the exception type in telemetry
3. Returning a safe `{"farmer": ["PASS"], "hands": [], "market": []}`

This ensures the agent never crashes the episode.

### Within the Decision Engine

Errors in candidate generation, filtering, or validation are caught
per-candidate. A failing candidate is simply removed from the candidate
list rather than crashing the entire pipeline.

### Within Services

Service methods raise specific exceptions (e.g., `CropServiceError`)
for domain-specific failures. The decision engine catches these and
excludes the affected action from candidates.

## Logging Errors

All errors are logged with:

- Exception type and message
- Full traceback (`exc_info=True`)
- Component and action context
- Turn and day (if available)

## Telemetry Integration

Every exception is recorded in telemetry:

```python
telemetry.record_exception(type(exc).__name__)
```

This allows post-hoc analysis of failure patterns.
