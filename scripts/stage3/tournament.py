#!/usr/bin/env python3
"""Stage 3 — tournament: champion vs hybrid / learned policies.

Runs ``--games`` full episodes per pairing with fresh seeds and reports the
reward delta.  The champion baseline is deterministic, so the meaningful test is
whether the learned policy improves over the champion on the *same* seeds.

Usage::

    python scripts/stage3/tournament.py --model-dir artifacts/models \\
        --policies champion,hybrid --games 3 --out-dir experiments/stage3/tournaments

Set ``KAG_RUNTIME_MODEL_DIR`` to the artifacts dir that holds the registered
bundle (defaults to ``artifacts/models``) so the hybrid/learned policy can load it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kaggle_environments import make  # noqa: E402

from agent.runtime.game import GameSnapshot  # noqa: E402
from agent.runtime.planner import TurnPlanner  # noqa: E402
from agent.runtime.policies import make_policy  # noqa: E402
from agent.runtime.settings import RuntimeSettings  # noqa: E402

POLICIES = ("champion", "hybrid", "learned")
OPPONENTS = ("random", "pass", "starter", "champion")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", default="", type=str)
    parser.add_argument("--policies", default="champion,hybrid", type=str)
    parser.add_argument("--games", default=3, type=int)
    parser.add_argument("--opponents", default="random,pass,starter", type=str)
    parser.add_argument("--out-dir", default="experiments/stage3/tournaments", type=str)
    return parser.parse_args()


def _plan_agent(planner: TurnPlanner) -> Callable[[Any, Any], dict[str, Any]]:
    def agent(obs: Any, configuration: Any = None) -> dict[str, Any]:
        return planner.plan(GameSnapshot.from_obs(obs)).action

    return agent


def _run_game(planner: TurnPlanner, opponent: str, seed: int) -> dict[int, float]:
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720, "seed": seed},
        debug=True,
    )
    agents: list[Callable[[Any, Any], dict[str, Any]] | str]
    if opponent == "champion":
        agents = [_plan_agent(planner), _plan_agent(planner)]
    else:
        agents = [_plan_agent(planner), opponent]
    env.run(agents)
    final = env.steps[-1]
    return {i: float(s.reward) for i, s in enumerate(final)}


def main() -> None:
    args = parse_args()
    policies = [p for p in args.policies.split(",") if p]
    opponents = [o for o in args.opponents.split(",") if o]
    for p in policies:
        if p not in POLICIES:
            raise SystemExit(f"unknown policy {p!r}; choose from {POLICIES}")

    if args.model_dir:
        os.environ["KAG_RUNTIME_MODEL_DIR"] = args.model_dir
    os.environ["KAG_RUNTIME_RECORD_EXPERIENCE"] = "false"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    started = time.time()

    for policy in policies:
        settings = RuntimeSettings.from_env()
        planner = TurnPlanner(settings=settings, policy=make_policy(policy, settings))
        for opponent in opponents:
            deltas: list[float] = []
            for seed in range(1, args.games + 1):
                rewards = _run_game(planner, opponent, seed)
                delta = rewards[0] - rewards[1]
                deltas.append(delta)
                print(
                    f"{policy} vs {opponent} s{seed}: p0={rewards[0]:.0f} "
                    f"p1={rewards[1]:.0f} diff={delta:+.0f}"
                )
            results[f"{policy} vs {opponent}"] = {
                "rewards": deltas,
                "mean": round(sum(deltas) / len(deltas), 1),
            }

    summary = {
        "model_dir": args.model_dir or os.environ.get("KAG_RUNTIME_MODEL_DIR", "artifacts/models"),
        "policies": policies,
        "opponents": opponents,
        "games_per_pairing": args.games,
        "results": results,
        "elapsed_s": round(time.time() - started, 2),
    }
    out_path = out_dir / "tournament_summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"wrote tournament summary to {out_path}")


if __name__ == "__main__":
    main()
