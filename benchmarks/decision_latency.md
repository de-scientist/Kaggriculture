# Decision Latency

## Targets

- Average: < 10 ms per decision
- P95: < 50 ms per decision
- P99: < 100 ms per decision

## Measurements

Run `python scripts/benchmark.py` to measure current latency.

### Current Results (Stage 1 Baseline)

Measured over 200 decisions on a minimal empty observation.

| Metric | Value | Target | Status |
|---|---|---|---|
| Average | 5.38 ms | < 10 ms | PASS |
| Median | 3.90 ms | — | PASS |
| Min | 2.06 ms | — | PASS |
| Max | 63.85 ms | — | PASS |
| P95 | 10.44 ms | < 50 ms | PASS |
| P99 | 52.49 ms | < 100 ms | PASS |
| Sample size | 200 | — | — |
