# Baseline Performance

## Decision Latency

| Metric | Value |
|---|---|
| Average latency | 5.38 ms |
| Median latency | 3.90 ms |
| Min latency | 2.06 ms |
| Max latency | 63.85 ms |
| P95 latency | 10.44 ms |
| P99 latency | 52.49 ms |

Measured over 200 decisions on a minimal observation. All well within
the 500 ms Kaggle decision timeout.

## Reward per Episode

| Opponent | Avg Reward | Std Dev |
|---|---|---|
| random | NOT MEASURED | NOT MEASURED |
| pass | NOT MEASURED | NOT MEASURED |

NOT MEASURED — Full episode replay requires `kaggle-environments` which
is not available in the current development environment.

## Actions per Turn

| Metric | Value |
|---|---|
| Average | ~1 (baseline strategy selects one action per turn) |
| Max | 1 farmer action + hand actions + market orders |

## Memory Usage

NOT MEASURED — Memory profiling not available in current environment.
Expected to be low (small domain objects, no large caches).
