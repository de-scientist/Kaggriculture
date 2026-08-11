#!/usr/bin/env python3
"""Stage 3 — collect experience episodes from the champion (and opponents).

Runs full 720-turn games against the built-in opponents (random / pass /
starter) and against itself (self-play) using the runtime policy, recording one
JSON row per turn into ``--out-dir`` via the managed :class:`ExperienceRecorder`.

Example::

    python scripts/stage3/collect_episodes.py --out-dir experiments/stage3/experiences \
        --seeds 1,2,3,4,5 --opponents random,pass,starter,champion
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kaggle_environments import make  # noqa: E402

from agent.learning.experience import ExperienceRecorder  # noqa: E402
from agent.runtime.game import GameSnapshot  # noqa: E402
from agent.runtime.planner import TurnPlanner  # noqa: E402
from agent.runtime.policies import make_policy  # noqa: E402
from agent.runtime.settings import RuntimeSettings  # noqa: E402

OPPONENTS = ("random", "pass", "starter", "champion")
POLICIES = ("champion", "hybrid", "learned")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="experiments/stage3/experiences", type=str)
    parser.add_argument("--seeds", default="1,2,3,4,5", type=str, help="comma-separated seeds")
    parser.add_argument("--opponents", default="random,pass,starter", type=str)
    parser.add_argument("--policy", default="champion", choices=POLICIES)
    parser.add_argument("--episode-steps", default=720, type=int)
    return parser.parse_args()


def _episode_id(prefix: str, seed: int) -> str:
    return f"{prefix}-s{seed}-{int(time.time())}"


def _run_managed(
    planner: TurnPlanner,
    recorder_p0: ExperienceRecorder,
    recorder_p1: ExperienceRecorder | None,
    game_id: str,
    seed: int,
    opponent: str,
    policy: str,
    episode_steps: int,
) -> dict[int, float]:
    """Run one episode with per-player managed recorders; returns final rewards."""
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": episode_steps, "seed": seed},
        debug=True,
    )
    episode_p0 = f"{game_id}-p0"
    meta = {"game_id": game_id, "seed": seed, "opponent": opponent, "policy": policy}
    recorder_p0.begin_episode(episode_p0, {**meta, "player": 0})
    if recorder_p1 is not None:
        recorder_p1.begin_episode(f"{game_id}-p1", {**meta, "player": 1})

    def make_agent(player: int) -> Callable[[Any, Any], dict[str, Any]]:
        recorder = recorder_p0 if player == 0 else recorder_p1
        if recorder is None:
            raise RuntimeError("player 1 recorder missing")

        def agent(obs: Any, configuration: Any = None) -> dict[str, Any]:
            snapshot = GameSnapshot.from_obs(obs)
            plan = planner.plan(snapshot)
            recorder.observe(snapshot, plan)
            return plan.action

        return agent

    if opponent == "champion":
        agents = [make_agent(0), make_agent(1)]
    else:
        agents = [make_agent(0), opponent]

    env.run(agents)
    final = env.steps[-1]
    rewards = {i: float(s.reward) for i, s in enumerate(final)}
    recorder_p0.end_episode({"outcome_money": rewards.get(0, 0.0)})
    if recorder_p1 is not None:
        recorder_p1.end_episode({"outcome_money": rewards.get(1, 0.0)})
    return rewards


def main() -> None:
    args = parse_args()
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    opponents = [o for o in args.opponents.split(",") if o.strip()]
    if not seeds:
        raise SystemExit("no seeds provided")
    for opp in opponents:
        if opp not in OPPONENTS:
            raise SystemExit(f"unknown opponent {opp!r}; choose from {OPPONENTS}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    settings = RuntimeSettings.from_env()
    planner = TurnPlanner(settings=settings, policy=make_policy(args.policy, settings))

    recorder_p0 = ExperienceRecorder(out_dir)
    recorder_p1 = ExperienceRecorder(out_dir)
    results: dict[str, dict[str, float]] = {}
    started = time.time()

    for opp in opponents:
        for seed in seeds:
            game_id = _episode_id(opp, seed)
            rewards = _run_managed(
                planner,
                recorder_p0,
                recorder_p1,
                game_id,
                seed,
                opp,
                args.policy,
                args.episode_steps,
            )
            results[f"{opp}-s{seed}"] = {"player0": rewards[0], "player1": rewards[1]}
            print(f"{opp} seed {seed}: reward p0={rewards[0]:.0f} p1={rewards[1]:.0f}")

    summary = {
        "policy": args.policy,
        "episode_steps": args.episode_steps,
        "seeds": seeds,
        "opponents": opponents,
        "results": results,
        "elapsed_s": round(time.time() - started, 2),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {len(results)} episodes to {out_dir} in {summary['elapsed_s']}s")


if __name__ == "__main__":
    main()
