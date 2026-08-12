#!/usr/bin/env python3
"""Quick benchmark for decision latency.

Runs the agent on a minimal observation multiple times and reports
latency statistics. Used to populate reports/stage_1_performance.md.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _minimal_obs(player: int = 0) -> dict:
    return {
        "player": player,
        "step": 0,
        "day": 0,
        "hour": 0,
        "remaining_turns": 720,
        "farms": [
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
        ],
        "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {}, "prices": {}},
        "town": {"unlocked_shops": []},
    }


def main() -> None:
    from agent.agent import agent

    obs = _minimal_obs()
    n = 200
    latencies: list[float] = []

    for _ in range(n):
        start = time.perf_counter()
        agent(obs)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        latencies.append(elapsed_ms)

    avg = statistics.mean(latencies)
    med = statistics.median(latencies)
    mn = min(latencies)
    mx = max(latencies)
    p95 = sorted(latencies)[int(n * 0.95)] if n > 1 else avg
    p99 = sorted(latencies)[int(n * 0.99)] if n > 1 else avg

    results = {
        "sample_size": n,
        "average_ms": round(avg, 3),
        "median_ms": round(med, 3),
        "min_ms": round(mn, 3),
        "max_ms": round(mx, 3),
        "p95_ms": round(p95, 3),
        "p99_ms": round(p99, 3),
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
