#!/usr/bin/env python3
"""Benchmark suite for the Kaggriculture AI agent (chapter 9 §204-209).

Measures decision latency across representative game states and writes
results to ``benchmarks/benchmark_results.json`` for CI artifact upload.

Metrics tracked:
  * Average decision latency
  * Median decision latency
  * P95 decision latency
  * P99 decision latency
  * Maximum decision latency

Usage:
    python scripts/benchmark.py
"""
from __future__ import annotations

import json
import statistics
import time
import tracemalloc
from datetime import datetime
from pathlib import Path

from agent.agent import agent
from tests.fixtures.observations import (
    minimal_observation,
    observation_advanced,
    observation_with_animal,
    observation_with_crop,
    observation_with_hands,
    observation_with_market,
    observation_with_seeds,
)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "benchmarks"
NUM_ITERATIONS = 100


def _collect_latency(observations: list[dict]) -> list[float]:
    latencies: list[float] = []
    for obs in observations:
        start = time.perf_counter()
        agent(obs)
        latencies.append((time.perf_counter() - start) * 1000)
    return latencies


def _percentile(data: list[float], pct: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int((pct / 100.0) * (len(sorted_data) - 1))
    return sorted_data[idx]


def _measure_memory(observations: list[dict]) -> float:
    tracemalloc.start()
    for obs in observations:
        agent(obs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024 / 1024  # MB


def benchmark_scenario(name: str, observations: list[dict]) -> dict:
    latencies = _collect_latency(observations)
    return {
        "name": name,
        "iterations": len(latencies),
        "average_ms": round(statistics.mean(latencies), 3),
        "median_ms": round(statistics.median(latencies), 3),
        "p95_ms": round(_percentile(latencies, 95), 3),
        "p99_ms": round(_percentile(latencies, 99), 3),
        "max_ms": round(max(latencies), 3),
        "min_ms": round(min(latencies), 3),
        "memory_peak_mb": round(_measure_memory(observations), 3),
    }


def build_observations() -> list[dict]:
    results = []
    for step in range(NUM_ITERATIONS):
        obs = minimal_observation()
        obs["step"] = step
        obs["day"] = step // 24
        obs["hour"] = step % 24
        results.append(obs)
    return results


def build_advanced_observations() -> list[dict]:
    results = []
    for step in range(NUM_ITERATIONS):
        obs = observation_advanced(day=7, money=6500.0)
        obs["step"] = step
        obs["farmer"] = [0, 0]
        results.append(obs)
    return results


def build_crop_observations() -> list[dict]:
    results = []
    for step in range(NUM_ITERATIONS):
        obs = observation_with_crop("WHEAT", planted_day=2)
        obs["step"] = step
        results.append(obs)
    return results


def build_animal_observations() -> list[dict]:
    results = []
    for step in range(NUM_ITERATIONS):
        obs = observation_with_animal("GOOSE")
        obs["step"] = step
        results.append(obs)
    return results


def build_market_observations() -> list[dict]:
    results = []
    for step in range(NUM_ITERATIONS):
        obs = observation_with_market(
            {"WHEAT": 25, "CARROT": 35, "STRAWBERRY": 75, "MELON": 100, "MILK": 50},
            {"WHEAT": 5000, "CARROT": 3000, "STRAWBERRY": 1000, "MELON": 500, "MILK": 200},
        )
        obs["step"] = step
        results.append(obs)
    return results


def build_seeds_observations() -> list[dict]:
    results = []
    for step in range(NUM_ITERATIONS):
        obs = observation_with_seeds({"WHEAT": 10, "CARROT": 5, "TOMATO": 3})
        obs["step"] = step
        results.append(obs)
    return results


def build_hands_observations() -> list[dict]:
    results = []
    for step in range(NUM_ITERATIONS):
        obs = observation_with_hands(4)
        obs["step"] = step
        results.append(obs)
    return results


def run_all_benchmarks() -> dict:
    scenarios = [
        ("minimal", build_observations),
        ("advanced", build_advanced_observations),
        ("with_crop", build_crop_observations),
        ("with_animal", build_animal_observations),
        ("with_market", build_market_observations),
        ("with_seeds", build_seeds_observations),
        ("with_hands", build_hands_observations),
    ]

    results = []
    for name, builder in scenarios:
        observations = builder()
        result = benchmark_scenario(name, observations)
        results.append(result)
        print(f"[{name}] avg={result['average_ms']}ms p95={result['p95_ms']}ms p99={result['p99_ms']}ms max={result['max_ms']}ms")

    baseline = results[0]
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "python_version": __import__("sys").version,
        "iterations_per_scenario": NUM_ITERATIONS,
        "scenarios": results,
        "baseline": {
            "average_ms": baseline["average_ms"],
            "p95_ms": baseline["p95_ms"],
            "p99_ms": baseline["p99_ms"],
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nResults written to {output_path}")

    _update_baseline_docs(results)

    return report


def _git_commit() -> str:
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()[:12] if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def _update_baseline_docs(results: list[dict]) -> None:
    baseline_md = OUTPUT_DIR / "baseline.md"
    lines = [
        "# Baseline Performance",
        "",
        f"Generated: {datetime.utcnow().isoformat()}",
        "",
        "## Decision Latency",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Average latency | {results[0]['average_ms']} ms |",
        f"| P95 latency | {results[0]['p95_ms']} ms |",
        f"| P99 latency | {results[0]['p99_ms']} ms |",
        f"| Max latency | {results[0]['max_ms']} ms |",
        "",
        "## Scenario Breakdown",
        "",
        "| Scenario | Avg (ms) | P95 (ms) | P99 (ms) | Max (ms) | Memory (MB) |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['name']} | {r['average_ms']} | {r['p95_ms']} | {r['p99_ms']} | {r['max_ms']} | {r['memory_peak_mb']} |"
        )
    lines.append("")
    baseline_md.write_text("\n".join(lines))


if __name__ == "__main__":
    report = run_all_benchmarks()
    baseline = report["baseline"]
    if baseline["p95_ms"] > 200:
        print(f"\nWARNING: P95 latency {baseline['p95_ms']}ms exceeds 200ms budget")
        exit(1)
    print(f"\nAll benchmarks passed. Avg={baseline['average_ms']}ms P95={baseline['p95_ms']}ms")
