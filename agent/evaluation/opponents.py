"""Diverse, mechanically-valid opponent agents for Stage 4B benchmarking.

Opponents are built from the production planner with different
``RuntimeSettings`` presets (or the built-in Kaggle strings ``"random"`` and
``"starter"``).  Every preset uses only behaviours the game actually supports,
so the benchmark never relies on invented mechanics.  Our own candidate agents
are wrapped in :class:`~agent.submission.failsafe.FailSafeAgent` so they survive
the Kaggle two-argument calling convention and contribute fallback telemetry.
"""

from __future__ import annotations

from typing import Any

from agent.runtime.agent import make_runtime_agent
from agent.runtime.settings import RuntimeSettings
from agent.submission.failsafe import FailSafeAgent

Agent = Any  # Callable[[obs], dict] | str

_BUILTIN: dict[str, str] = {"random": "random", "starter": "starter"}

_PRESETS: dict[str, dict[str, Any]] = {
    "conservative": dict(
        reserve_money=800.0,
        target_hands=(1, 2, 2, 2),
        land_budget_ratio=5.0,
        melon_max_tiles=0,
        enable_animals=False,
    ),
    "aggressive": dict(
        reserve_money=50.0,
        target_hands=(5, 6, 7, 8),
        land_budget_ratio=1.2,
        enable_animals=True,
        cow_max=4,
        goose_max=2,
        melon_max_tiles=12,
    ),
    "expansion": dict(
        land_latest_day=(20, 14, 8),
        target_hands=(4, 5, 6, 7),
        reserve_money=100.0,
        land_budget_ratio=1.5,
        enable_animals=True,
        cow_max=2,
        goose_max=1,
    ),
    "production": dict(
        target_hands=(3, 4, 4, 5),
        melon_max_tiles=10,
        reserve_money=200.0,
        enable_animals=True,
        cow_max=3,
        goose_max=1,
    ),
    "market": dict(
        sell_min_ratio=0.7,
        reserve_money=300.0,
        target_hands=(3, 4, 5, 6),
    ),
    "balanced": dict(),
}


def available_opponents() -> list[str]:
    """Names that can be used as benchmark opponents."""
    return [*_BUILTIN.keys(), *_PRESETS.keys()]


def build_opponent(name: str) -> Agent:
    """Return an opponent agent by name.

    Built-in Kaggle opponents are returned as their string identifier; preset
    opponents are wrapped production agents.
    """
    if name in _BUILTIN:
        return _BUILTIN[name]
    if name in _PRESETS:
        settings = RuntimeSettings(**_PRESETS[name])
        return FailSafeAgent(make_runtime_agent("auto", settings=settings))
    raise ValueError(f"unknown opponent: {name!r}")


def opponent_profile(name: str) -> str:
    """Human-readable description of an opponent's actual behaviour."""
    profiles = {
        "random": "Built-in random agent (no economic strategy).",
        "starter": "Built-in deterministic Kaggle baseline.",
        "conservative": "High cash reserve, few workers, no melon/animals, late land.",
        "aggressive": "Low reserve, many workers, animals + melon enabled, early land.",
        "expansion": "Land bought early, many workers, animals enabled.",
        "production": "Crop-focused with moderate animals and melon.",
        "market": "Sells aggressively at lower price thresholds.",
        "balanced": "Default champion planner settings.",
    }
    return profiles.get(name, "unknown")
