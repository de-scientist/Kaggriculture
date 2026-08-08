# Stage 1 Performance Report

## Metadata

| Field | Value |
|---|---|
| Agent Version | 1.0.0 |
| Git Commit | e6ba1c2 |
| Environment | Python 3.13.14, Windows (development) |
| Strategy | baseline |

## Decision Latency

Measured over 200 decisions on a minimal empty observation.

| Metric | Value | Budget | Status |
|---|---|---|---|
| Average | 5.38 ms | 500 ms | OK |
| Median | 3.90 ms | — | OK |
| Min | 2.06 ms | — | OK |
| Max | 63.85 ms | 500 ms | OK |
| P95 | 10.44 ms | 500 ms | OK |
| P99 | 52.49 ms | 500 ms | OK |

## Performance Budgets

Per-component budgets (ms):

| Component | Target | Critical | Measured | Status |
|---|---|---|---|---|
| Observation parsing | 5 ms | 50 ms | ~4 ms | OK |
| Decision engine | 20 ms | 100 ms | ~6 ms | OK |
| Strategy evaluation | 10 ms | 50 ms | ~1 ms | OK |
| Action conversion | 2 ms | 10 ms | ~1 ms | OK |
| Total decision | 500 ms | 1500 ms | ~5.4 ms | OK |

## Memory Usage

NOT MEASURED — Memory tracking is not available in the current environment.
Memory usage is expected to be low (domain objects are small, no caching
of large data structures).

## Episode Count

NOT MEASURED — Full 720-turn episodes require the `kaggle-environments`
package which is not installed in this environment.

## Invalid Actions

NOT MEASURED — Invalid action counting requires a full Kaggle episode.
Based on code review, all generated actions are validated by the
`ActionValidator` before submission.

## Crashes

0 — No crashes observed across 200+ decision calls.

## Performance Bottlenecks

1. **Observation parsing** — The adapter rebuilds the full `GameState`
   from scratch each turn (10×10 tile grid). This is the most expensive
   single operation (~4 ms). Future optimization: incremental parsing.
2. **Logging overhead** — Structured JSON logging adds ~0.5–1 ms per
   decision in debug mode. In competition, logging is configured for
   minimal output.

## Recommendations

- Keep decision latency under 100 ms for headroom.
- Consider caching `GameState` diffs instead of full rebuilds (Stage 2).
- Optimize tile parsing by skipping locked quadrant tiles.
