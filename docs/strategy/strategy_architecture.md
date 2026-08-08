# Strategy Architecture

## Overview

The strategy layer (`agent/strategies/`) contains replaceable decision
algorithms. The Stage 1 baseline uses a deterministic rule-based approach
with a weighted scoring model.

## Components

```
StrategyEngine
        ↓
BaselineStrategy
        ├── ActionGenerator (generates candidates)
        ├── ActionFilter (removes illegal actions)
        ├── ActionValidator (validates legality)
        └── Scoring Model (scores and ranks candidates)
```

## Strategy Interface

All strategies implement the same interface:

```python
class BaseStrategy:
    def generate_candidates(self, context: DecisionContext) -> list[CandidateAction]
    def filter(self, candidates: list[CandidateAction], context: DecisionContext) -> list[CandidateAction]
    def validate(self, candidates: list[CandidateAction], context: DecisionContext) -> list[CandidateAction]
    def score(self, action: CandidateAction) -> float
    def select(self, context: DecisionContext) -> dict
```

## Stage 1 Strategy

- **Name:** `baseline`
- **Type:** Rule-based, deterministic
- **Scoring:** Weighted sum of 8 factors
- **Fallback:** Always falls back to `PASS`
- **Determinism:** Identical observations produce identical actions
