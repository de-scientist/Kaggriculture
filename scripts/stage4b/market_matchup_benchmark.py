"""Stage 4B — Market Matchup Investigation.

Runs the frozen Champion (player 0) against the ``market`` opponent (player 1)
across multiple reproducible seeds, capturing the richest telemetry the
environment actually exposes (per-step farm state, private shed, market prices
and inventory, town demand, and both players' actions).

Nothing here modifies the Champion. It only observes games.

Outputs:
  artifacts/championship/MARKET_MATCHUP_TELEMETRY/seed_NNN.json   (per game)
  artifacts/championship/MARKET_MATCHUP_RESULTS.json              (aggregate)
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Allow running from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main  # frozen Champion via main.agent  # noqa: E402
from agent.evaluation.opponents import build_opponent  # noqa: E402

ART = Path("artifacts/championship")
TEL_DIR = ART / "MARKET_MATCHUP_TELEMETRY"
SEEDS = list(range(12))
EPISODE_STEPS = 720
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]


def _count_tiles(farm: dict) -> dict:
    """Derive land/animal/crop metrics from a farm's tile grid."""
    land = len(farm.get("unlocked_quadrants", []))
    workers = 1 + len(farm.get("hands", []))
    animals = 0
    animal_by = Counter()
    planted_total = 0
    crop_by = Counter()
    mature = 0
    coops = pastures = 0
    for row in farm.get("tiles", []):
        for tile in row:
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "PLANT":
                planted_total += 1
                crop_by[tile.get("crop")] += 1
                if tile.get("yield_units", 0) and tile.get("yield_units", 0) > 0:
                    mature += 1
            elif kind in ("COOP", "PASTURE"):
                if kind == "COOP":
                    coops += 1
                else:
                    pastures += 1
                a = tile.get("animal")
                if a:
                    animals += 1
                    animal_by[a] += 1
    return {
        "land": land,
        "workers": workers,
        "animals": animals,
        "animal_by": dict(animal_by),
        "planted_total": planted_total,
        "crop_by": dict(crop_by),
        "mature": mature,
        "coops": coops,
        "pastures": pastures,
    }


def _parse_actions(action: dict) -> dict:
    """Extract strategic events from a returned action dict."""
    events = []
    market_ops = action.get("market", []) or []
    farmer_ops = [action.get("farmer")] if action.get("farmer") else []
    hands_ops = action.get("hands", []) or []
    all_unit = farmer_ops + hands_ops
    for op in all_unit:
        if not isinstance(op, list) or not op:
            continue
        head = op[0]
        if head == "PLANT":
            events.append(("PLANT", op[1] if len(op) > 1 else None))
        elif head == "FERTILIZE":
            events.append(("FERTILIZE", None))
        elif head == "COLLECT_FERTILIZER":
            events.append(("COLLECT_FERTILIZER", None))
        elif head == "CARE":
            events.append(("CARE", None))
        elif head == "FEED":
            events.append(("FEED", None))
        elif head == "BUILD_COOP":
            events.append(("BUILD_COOP", None))
        elif head == "BUILD_PASTURE":
            events.append(("BUILD_PASTURE", None))
    for op in market_ops:
        if not isinstance(op, list) or not op:
            continue
        head = op[0]
        if head == "BUY_LAND":
            events.append(("BUY_LAND", None))
        elif head == "HIRE":
            events.append(("HIRE", None))
        elif head == "BUY_ANIMAL":
            events.append(("BUY_ANIMAL", op[1] if len(op) > 1 else None))
        elif head == "BUY_SEED":
            events.append(("BUY_SEED", op[1] if len(op) > 1 else None, op[2] if len(op) > 2 else None))
        elif head == "BUY_PRODUCT":
            events.append(("BUY_PRODUCT", op[1] if len(op) > 1 else None, op[2] if len(op) > 2 else None))
        elif head == "SELL":
            n = op[2] if len(op) > 2 else None
            events.append(("SELL", op[1] if len(op) > 1 else None, n))
    return events


def run_game(seed: int) -> dict:
    from kaggle_environments import make

    opponent = build_opponent("market")
    env = make("kaggriculture", configuration={"episodeSteps": EPISODE_STEPS, "seed": seed}, debug=True)
    env.run([main.agent, opponent])

    per_step = defaultdict(list)
    daily = []
    events = []
    first_plant = {0: set(), 1: set()}
    cum = {0: Counter(), 1: Counter()}
    last_day = -1
    latest = {0: None, 1: None}  # most recent per-player metrics within a step

    for t, step in enumerate(env.steps):
        for p in (0, 1):
            obs = step[p].observation
            act = step[p].action
            farm = obs["farms"][p]
            priv = obs.get("private", {})
            tile_metrics = _count_tiles(farm)
            money = float(farm["money"])
            latest[p] = (tile_metrics, money, priv, obs)

            per_step[f"p{p}_money"].append(money)
            per_step[f"p{p}_land"].append(tile_metrics["land"])
            per_step[f"p{p}_workers"].append(tile_metrics["workers"])
            per_step[f"p{p}_animals"].append(tile_metrics["animals"])
            per_step[f"p{p}_planted"].append(tile_metrics["planted_total"])
            per_step[f"p{p}_mature"].append(tile_metrics["mature"])

            # shed total (private inventory of harvested goods)
            shed = priv.get("shed", {}) if isinstance(priv, dict) else {}
            shed_total = sum(shed.values()) if isinstance(shed, dict) else 0

            day = obs.get("day", 0)
            hour = obs.get("hour", 0)

            # record events
            for ev in _parse_actions(act or {}):
                etype = ev[0]
                cum[p][etype] += 1
                if etype == "PLANT" and ev[1] not in first_plant[p]:
                    first_plant[p].add(ev[1])
                    events.append({"step": t, "day": day, "hour": hour, "player": p,
                                   "type": "FIRST_PLANT", "detail": ev[1]})
                if etype == "BUY_LAND":
                    events.append({"step": t, "day": day, "hour": hour, "player": p,
                                   "type": "BUY_LAND", "detail": farm.get("unlocked_quadrants")})
                if etype == "HIRE":
                    events.append({"step": t, "day": day, "hour": hour, "player": p,
                                   "type": "HIRE", "detail": farm.get("hires_today")})
                if etype == "BUY_ANIMAL":
                    events.append({"step": t, "day": day, "hour": hour, "player": p,
                                   "type": "BUY_ANIMAL", "detail": ev[1]})
                if etype == "SELL" and ev[2] is not None:
                    n = ev[2]
                    # log large sells and all end-game sells
                    if n >= 5 or day >= 26:
                        events.append({"step": t, "day": day, "hour": hour, "player": p,
                                       "type": "SELL", "detail": {"item": ev[1], "n": n}})
                if etype == "FERTILIZE":
                    events.append({"step": t, "day": day, "hour": hour, "player": p,
                                   "type": "FERTILIZE", "detail": None})
                if etype == "COLLECT_FERTILIZER":
                    events.append({"step": t, "day": day, "hour": hour, "player": p,
                                   "type": "COLLECT_FERTILIZER", "detail": None})
                if etype == "CARE":
                    events.append({"step": t, "day": day, "hour": hour, "player": p,
                                   "type": "CARE", "detail": None})

            # daily snapshot at hour 0 (capture both players from latest metrics)
            if hour == 0 and day != last_day and latest[0] is not None and latest[1] is not None:
                last_day = day
                market = obs.get("market", {})
                town = obs.get("town", {})
                m0, money0, priv0, _ = latest[0]
                m1, money1, priv1, _ = latest[1]
                shed0 = priv0.get("shed", {}) if isinstance(priv0, dict) else {}
                shed1 = priv1.get("shed", {}) if isinstance(priv1, dict) else {}
                daily.append({
                    "step": t, "day": day,
                    "p0_money": money0,
                    "p1_money": money1,
                    "p0_land": m0["land"],
                    "p1_land": m1["land"],
                    "p0_workers": m0["workers"],
                    "p1_workers": m1["workers"],
                    "p0_animals": m0["animals"],
                    "p1_animals": m1["animals"],
                    "p0_planted": m0["planted_total"],
                    "p1_planted": m1["planted_total"],
                    "p0_crop_by": m0["crop_by"],
                    "p0_animal_by": m0["animal_by"],
                    "p0_shed_total": sum(shed0.values()),
                    "p1_shed_total": sum(shed1.values()),
                    "p0_shed": dict(shed0),
                    "p1_shed": dict(shed1),
                    "market_prices": dict(market.get("prices", {})),
                    "market_inventory": dict(market.get("inventory", {})),
                    "town_shops": list(town.get("unlocked_shops", [])),
                })

    final = env.steps[-1]
    champ_coins = float(final[0].reward if final[0].reward is not None else final[0].observation["farms"][0]["money"])
    market_coins = float(final[1].reward if final[1].reward is not None else final[1].observation["farms"][0]["money"])
    winner = 0 if champ_coins > market_coins else (1 if market_coins > champ_coins else -1)

    return {
        "seed": seed,
        "winner": winner,
        "champ_coins": champ_coins,
        "market_coins": market_coins,
        "margin": champ_coins - market_coins,
        "per_step": {k: v for k, v in per_step.items()},
        "daily": daily,
        "events": events,
        "first_plant": {str(k): sorted(v) for k, v in first_plant.items()},
        "cum_events": {str(k): dict(cum[k]) for k in cum},
    }


def main_cli() -> int:
    TEL_DIR.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)

    games = []
    for seed in SEEDS:
        g = run_game(seed)
        (TEL_DIR / f"seed_{seed:03d}.json").write_text(json.dumps(g, separators=(",", ":")))
        wl = "WIN" if g["winner"] == 0 else ("loss" if g["winner"] == 1 else "TIE")
        print(f"seed {seed:2d}: champ {g['champ_coins']:.0f}  market {g['market_coins']:.0f}  {wl}", flush=True)
        games.append(g)

    wins = sum(1 for g in games if g["winner"] == 0)
    losses = sum(1 for g in games if g["winner"] == 1)
    ties = sum(1 for g in games if g["winner"] == -1)
    champ_coins = [g["champ_coins"] for g in games]
    margins = [g["margin"] for g in games]

    aggregate = {
        "benchmark": "Champion (auto/ChampionPolicy) vs market opponent",
        "seeds": SEEDS,
        "games": len(games),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "win_rate": wins / len(games),
        "avg_champ_coins": statistics.mean(champ_coins),
        "median_champ_coins": statistics.median(champ_coins),
        "avg_market_coins": statistics.mean(g["market_coins"] for g in games),
        "median_market_coins": statistics.median(g["market_coins"] for g in games),
        "avg_margin": statistics.mean(margins),
        "median_margin": statistics.median(margins),
        "best_game": max(games, key=lambda g: g["champ_coins"])["seed"],
        "worst_game": min(games, key=lambda g: g["champ_coins"])["seed"],
        "games_detail": [
            {"seed": g["seed"], "winner": g["winner"], "champ_coins": g["champ_coins"],
             "market_coins": g["market_coins"], "margin": g["margin"]}
            for g in games
        ],
    }
    (ART / "MARKET_MATCHUP_RESULTS.json").write_text(json.dumps(aggregate, indent=2))
    print(json.dumps(aggregate, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main_cli())
