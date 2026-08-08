# Performance Testing

## Overview

Performance tests verify that the agent meets timing budgets and has no
critical performance regressions. They are located in
`tests/unit/test_determinism.py` and `tests/performance/`.

## Performance Budgets

| Component | Target | Critical (Failure) |
|---|---|---|
| Observation parsing | 5 ms | 50 ms |
| Decision engine | 20 ms | 100 ms |
| Strategy evaluation | 10 ms | 50 ms |
| Action conversion | 2 ms | 10 ms |
| Total decision | 500 ms | 1500 ms |

## What Is Tested

| Test | Description |
|---|---|
| `test_decision_latency_within_budget` | Single decision completes within target |
| `test_performance_budget_critical` | Duration exceeding failure threshold → CRITICAL status |
| `test_decision_latency_p95_under_budget` | P95 latency within target |
| `test_memory_stable_over_many_decisions` | No memory growth over 500 decisions |
| `test_no_performance_regression_vs_baseline` | Latency does not regress vs. known baseline |

## Running Performance Tests

```bash
# All tests (performance tests are included)
pytest

# Performance only (when markers are added)
pytest -m performance
```

## Benchmarking

Run the benchmark script:

```bash
python benchmarks/benchmark.py
```

This measures:

- Average decision latency
- P95/P99 decision latency
- Memory usage
- Full episode duration

## Profiling

```bash
python -m cProfile -o profile.pstats main.py
python -c "import pstats; pstats.Stats('profile.pstats').sort_stats('cumulative').print_stats(30)"
```

Or use the built-in profiler:

```bash
python scripts/profile.py
```
