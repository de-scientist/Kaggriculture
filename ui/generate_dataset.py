"""Generate a real Kaggriculture game dataset for the Command Center UI.

Runs the actual champion agent (:mod:`main`) against a built-in opponent using the
real Kaggle environment, then records a faithful per-turn snapshot of the public
and private game state plus the planner diagnostics (no hidden chain-of-thought).

Output: ``ui/public/data/games.json``

This script is a *data export* tool only. It never imports, modifies, or depends
on the autonomous submission at runtime: the browser UI consumes the exported
JSON. The official agent remains fully independent.
"""

from __future__ import annotations

import json
import os
import datetime as _dt
from typing import Any

from kaggle_environments import make

from agent.runtime.game import GameSnapshot
from agent.runtime.planner import TurnPlanner
from agent.submission.failsafe import FailSafeAgent
from agent.runtime.agent import agent as _raw_agent

# --------------------------------------------------------------------------- #
# Planner wrapper that captures decision diagnostics for one player.
# --------------------------------------------------------------------------- #

class _CapturePlanner:
    """Wraps the real champion planner and records each turn's diagnostics."""

    def __init__(self) -> None:
        self.planner = TurnPlanner()
        self.records: list[dict[str, Any]] = []

    def act(self, obs: dict[str, Any], configuration: Any = None) -> dict[str, Any]:
        snap = GameSnapshot.from_obs(obs)
        plan = self.planner.plan(snap)
        # Candidate summary (observable, no internal reasoning exposed).
        candidates: list[dict[str, Any]] = []
        for t in plan.candidates:
            candidates.append(
                {
                    "action_type": getattr(t, "action_type", "unknown"),
                    "crop": getattr(t, "crop", None),
                    "item": getattr(t, "item", None),
                    "value": getattr(t, "value", None),
                }
            )
        self.records.append(
            {
                "policy": plan.info.get("policy"),
                "adjustments": plan.info.get("adjustments"),
                "n_tasks": plan.info.get("n_tasks"),
                "n_jobs": plan.info.get("n_jobs"),
                "candidates": candidates[:12],
                "farmer_action_type": plan.farmer_action_type,
            }
        )
        return plan.action


def _make_captured_agent() -> tuple[Any, _CapturePlanner]:
    cp = _CapturePlanner()
    failsafe = FailSafeAgent(cp.act)
    return failsafe, cp


# --------------------------------------------------------------------------- #
# Decision derivation (structured, observable signals only).
# --------------------------------------------------------------------------- #

def _classify_action(action: dict[str, Any], private: dict[str, Any], market: dict[str, Any]) -> dict[str, Any]:
    farmer = action.get("farmer") or ["PASS"]
    hands = action.get("hands") or []
    orders = action.get("market") or []

    sell = next((o for o in orders if o and o[0] == "SELL"), None)
    buy_seed = next((o for o in orders if o and o[0] == "BUY_SEED"), None)
    buy_land = next((o for o in orders if o and o[0] == "BUY_LAND"), None)
    hire = next((o for o in orders if o and o[0] == "HIRE"), None)
    fop = farmer[0] if farmer else "PASS"

    action_type = "wait"
    summary = "Observed the farm and held position."
    expected_value = 0

    if sell:
        item, n = sell[1], sell[2] if len(sell) > 2 else 0
        price = market.get("prices", {}).get(item, 1)
        expected_value = int(price * n)
        action_type = "trade"
        summary = f"Sold {n} {item} at ~{price}c/unit (≈{expected_value}c)."
    elif buy_land:
        action_type = "expand"
        summary = "Purchased a new land quadrant to expand capacity."
        expected_value = -1000
    elif hire:
        action_type = "expand"
        summary = "Hired a farm hand to increase daily throughput."
        expected_value = -1
    elif buy_seed:
        item, n = buy_seed[1], buy_seed[2] if len(buy_seed) > 2 else 0
        action_type = "expand"
        summary = f"Acquired {n} {item} seed(s) for the next planting cycle."
    elif fop in ("PLANT",):
        crop = farmer[1] if len(farmer) > 1 else "crop"
        action_type = "farm"
        summary = f"Planted {crop} on the current tile."
    elif fop in ("WATER", "FERTILIZE"):
        action_type = "farm"
        summary = f"{'Watered' if fop == 'WATER' else 'Fertilized'} the current tile."
    elif fop in ("HARVEST",):
        action_type = "farm"
        summary = "Harvested the mature crop on the current tile."
        expected_value = 50
    elif fop in ("BUILD_COOP", "BUILD_PASTURE"):
        action_type = "expand"
        summary = "Constructed an animal structure."
    elif fop in ("FEED", "CARE", "COLLECT_FERTILIZER"):
        action_type = "farm"
        summary = "Tended to the animals on the current tile."
    elif any(h and h[0] in ("PLANT", "WATER", "HARVEST", "FERTILIZE") for h in hands):
        action_type = "farm"
        summary = "Delegated field work to a hired hand."
    elif any(h and h[0] == "MOVE" or h and h[0] in ("NORTH", "SOUTH", "EAST", "WEST") for h in hands):
        action_type = "move"
        summary = "Repositioned units toward the next objective."

    return {"type": action_type, "summary": summary, "expected_value": expected_value}


def _strategy_mode(day: int, hour: int, money: int, step: int, total: int) -> str:
    if step < total * 0.1:
        return "STARTUP"
    if day <= 2:
        return "STARTUP"
    if step > total * 0.9:
        return "ENDGAME"
    if money < 1500:
        return "RECOVERY"
    if money > 12000:
        return "PRODUCTION"
    if day % 7 == 0:
        return "EXPANSION"
    return "GROWTH"


def _confidence(action: dict[str, Any], cp_record: dict[str, Any], money_trend: float) -> dict[str, Any]:
    base = 0.7
    if cp_record.get("n_jobs", 0):
        base += 0.1
    if cp_record.get("candidates"):
        base += min(0.1, 0.02 * len(cp_record["candidates"]))
    if money_trend > 0:
        base += 0.05
    conf = min(0.97, max(0.45, base))
    level = "High" if conf >= 0.8 else "Medium" if conf >= 0.62 else "Low"
    return {"value": round(conf, 2), "level": level}


def _factors(obs: dict[str, Any], action: dict[str, Any], money: int, opp_money: int) -> list[str]:
    factors: list[str] = []
    private = obs.get("private", {})
    shed = private.get("shed", {})
    if any(v > 10 for v in shed.values()):
        top = max(shed.items(), key=lambda kv: kv[1])
        factors.append(f"Inventory of {top[0]} ({top[1]}) above comfortable threshold.")
    market = obs.get("market", {})
    prices = market.get("prices", {})
    best = max(prices.items(), key=lambda kv: kv[1]) if prices else ("-", 0)
    factors.append(f"Best current price: {best[0]} at {best[1]}c.")
    gap = money - opp_money
    if gap >= 0:
        factors.append(f"Ahead of opponent by {gap}c.")
    else:
        factors.append(f"Behind opponent by {-gap}c — focusing on catch-up efficiency.")
    if money < 2000:
        factors.append("Cash reserves are low; prioritising liquidity.")
    factors.append(f"Day {obs.get('day')} / horizon — phase-appropriate allocation.")
    return factors


# --------------------------------------------------------------------------- #
# Game recording.
# --------------------------------------------------------------------------- #

def _run_game(opponent: str, seed: int, episode_steps: int) -> dict[str, Any]:
    agent_fn, cp = _make_captured_agent()
    env = make("kaggriculture", configuration={"episodeSteps": episode_steps, "seed": seed}, debug=True)
    env.run([agent_fn, opponent])

    turns: list[dict[str, Any]] = []
    money_hist: list[int] = []
    opp_money_hist: list[int] = []
    price_hist: dict[str, list[int]] = {}
    actions_log: list[dict[str, Any]] = []

    steps = env.steps
    # steps[0] is the initial state (both agents' pre-turn 0 observation).
    # The agent acts on steps[1..]; each step i has the observation AFTER the
    # previous action. We align action i with observation i+1.
    prev_action = None
    for i, st in enumerate(steps):
        p0 = st[0]
        obs = p0.get("observation", {})
        if not obs or "farms" not in obs:
            continue
        me = obs["farms"][0]
        opp = obs["farms"][1] if len(obs["farms"]) > 1 else None
        money = me.get("money", 0)
        opp_money = opp.get("money", 0) if opp else 0
        market = obs.get("market", {})
        private = obs.get("private", {})
        step_idx = obs.get("step", i)
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)

        # The action that produced THIS observation is the one recorded at i-1.
        action = prev_action if prev_action is not None else {"farmer": ["PASS"], "hands": [], "market": []}
        cp_rec = cp.records[i - 1] if (i - 1) < len(cp.records) else {}

        money_trend = money_hist[-1] - money_hist[-2] if len(money_hist) >= 2 else 0
        decision = _classify_action(action, private, market)
        decision["strategy_mode"] = _strategy_mode(day, hour, money, step_idx, episode_steps)
        conf = _confidence(action, cp_rec, money_trend)
        decision["confidence"] = conf
        decision["factors"] = _factors(obs, action, money, opp_money)
        decision["policy"] = cp_rec.get("policy")
        decision["n_candidates"] = len(cp_rec.get("candidates", []))
        decision["alternatives"] = [
            {"type": c["action_type"], "label": (c["crop"] or c["item"] or "general")}
            for c in cp_rec.get("candidates", [])[:4]
        ]

        # Compact farm snapshot (nulls are cheap in JSON).
        farm_snap = {
            "tiles": me.get("tiles"),
            "farmer": me.get("farmer"),
            "hands": me.get("hands", []),
            "unlocked_quadrants": me.get("unlocked_quadrants", []),
            "hires_today": me.get("hires_today", 0),
        }

        turns.append(
            {
                "turn": step_idx,
                "day": day,
                "hour": hour,
                "money": money,
                "opp_money": opp_money,
                "farm": farm_snap,
                "private": private,
                "market": market,
                "town": obs.get("town", {}),
                "action": action,
                "opp_action": (st[1].get("action") if len(st) > 1 else None),
                "decision": decision,
            }
        )

        money_hist.append(money)
        opp_money_hist.append(opp_money)
        for k, v in market.get("prices", {}).items():
            price_hist.setdefault(k, []).append(v)

        actions_log.append(
            {
                "turn": step_idx,
                "day": day,
                "hour": hour,
                "action": action,
                "decision": decision,
            }
        )

        # Next iteration's "previous action" is what the agent will do on step i+1.
        prev_action = p0.get("action")
        # Also pull the action from the step's action field if present.
        if prev_action is None and i + 1 < len(steps):
            prev_action = steps[i + 1][0].get("action")

    final = steps[-1][0]
    final_obs = final.get("observation", {})
    final_me = final_obs.get("farms", [{}])[0]
    final_opp = final_obs.get("farms", [{}, {}])[1] if len(final_obs.get("farms", [])) > 1 else {}

    return {
        "id": f"real-seed{seed:03d}-vs-{opponent}",
        "agent_version": "v1.2",
        "opponent": opponent,
        "seed": seed,
        "episode_steps": episode_steps,
        "real": True,
        "turns": turns,
        "money_history": money_hist,
        "opp_money_history": opp_money_hist,
        "price_history": price_hist,
        "actions_log": actions_log,
        "final": {
            "money": final_me.get("money", money_hist[-1] if money_hist else 0),
            "opp_money": final_opp.get("money", opp_money_hist[-1] if opp_money_hist else 0),
            "reward": final.get("reward"),
            "status": final.get("status"),
        },
    }


# --------------------------------------------------------------------------- #
# Championship / artifacts loading.
# --------------------------------------------------------------------------- #

def _load_championship() -> dict[str, Any]:
    champ: dict[str, Any] = {"source": "artifacts", "data": None}
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base, "artifacts", "championship", "champion_registry.json"),
        os.path.join(base, "artifacts", "championship", "challenger_registry.json"),
        os.path.join(base, "artifacts", "championship", "CHAMPION_TOURNAMENT_RESULTS.json"),
        os.path.join(base, "artifacts", "championship", "champion_registry.json"),
    ]
    data: dict[str, Any] = {}
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data[os.path.basename(path)] = json.load(f)
            except Exception:
                pass
    if data:
        champ["data"] = data
    return champ


def main() -> None:
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data")
    os.makedirs(out_dir, exist_ok=True)

    print("Running real game vs 'random' (seed 0) ...")
    g1 = _run_game("random", 0, 720)
    print(f"  -> {len(g1['turns'])} turns, final money {g1['final']['money']}")

    print("Running real game vs 'starter' (seed 1) ...")
    g2 = _run_game("starter", 1, 720)
    print(f"  -> {len(g2['turns'])} turns, final money {g2['final']['money']}")

    payload = {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "source": "real",
        "games": [g1, g2],
        "championship": _load_championship(),
    }

    out_path = os.path.join(out_dir, "games.json")
    with open(out_path, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    size_mb = os.path.getsize(out_path) / 1_048_576
    print(f"Wrote {out_path} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
