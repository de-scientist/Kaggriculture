"""H-MARKET-1 controlled challenger experiment.

Runs Champion v1.1 and a sweep of H-MARKET-1 configurations against the
deterministic ``market`` opponent across the 12 fixed seeds, collecting the full
metric set required by the experiment spec.  The frozen Champion is never
modified; the challenger only overrides RuntimeSettings via HMarket1Policy.

Outputs:
  experiments/h_market_1/{README.md,config.json,benchmark_results.json,
                          benchmark_report.md,analysis.md,telemetry/}
  docs/experiments/H_MARKET_1_MARKET_ANALYSIS.md
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import main  # noqa: E402
from agent.evaluation.opponents import build_opponent  # noqa: E402
from agent.runtime.agent import make_runtime_agent  # noqa: E402
from agent.runtime.policies import ChampionPolicy, HMarket1Policy  # noqa: E402
from agent.submission.failsafe import FailSafeAgent  # noqa: E402

ART = Path("experiments/h_market_1")
TEL = ART / "telemetry"
SEEDS = list(range(12))
EPISODE_STEPS = 720
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]

CHALLENGER_SWEEP = [
    ("low_off", dict(melon_profile="low", fertilizer_mode="off")),
    ("medium_off", dict(melon_profile="medium", fertilizer_mode="off")),
    ("high_off", dict(melon_profile="high", fertilizer_mode="off")),
    ("medium_melon", dict(melon_profile="medium", fertilizer_mode="melon")),
]


def _count_melon_tiles(farm: dict) -> int:
    n = 0
    for row in farm.get("tiles", []):
        if isinstance(row, list):
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                    n += 1
    return n


def _count_animals(farm: dict) -> int:
    n = 0
    for row in farm.get("tiles", []):
        if isinstance(row, list):
            for t in row:
                if isinstance(t, dict) and "animal" in t and t.get("animal"):
                    n += 1
    return n


def _parse_actions(action: dict, player: int, day: int, hour: int, step: int, events: list) -> None:
    market_ops = action.get("market", []) or []
    unit_ops = [action.get("farmer")] + (action.get("hands", []) or [])
    for op in unit_ops:
        if not isinstance(op, list) or not op:
            continue
        h = op[0]
        if h == "PLANT" and len(op) > 1:
            if op[1] == "MELON":
                events.append({"player": player, "day": day, "hour": hour, "step": step,
                               "type": "PLANT_MELON"})
        elif h == "FERTILIZE":
            events.append({"player": player, "day": day, "hour": hour, "step": step,
                           "type": "FERTILIZE"})
        elif h == "BUY_LAND":
            events.append({"player": player, "day": day, "hour": hour, "step": step,
                           "type": "BUY_LAND"})
        elif h == "HIRE":
            events.append({"player": player, "day": day, "hour": hour, "step": step,
                           "type": "HIRE"})
    for op in market_ops:
        if not isinstance(op, list) or not op:
            continue
        h = op[0]
        if h == "SELL" and len(op) > 2:
            events.append({"player": player, "day": day, "hour": hour, "step": step,
                           "type": "SELL", "item": op[1], "n": op[2]})
        elif h == "BUY_PRODUCT" and len(op) > 1 and op[1] == "FERTILIZER":
            events.append({"player": player, "day": day, "hour": hour, "step": step,
                           "type": "BUY_FERTILIZER", "n": op[2] if len(op) > 2 else 1})


def run_game(agent, seed: int, label: str) -> dict:
    from kaggle_environments import make

    opponent = build_opponent("market")
    env = make("kaggriculture", configuration={"episodeSteps": EPISODE_STEPS, "seed": seed}, debug=True)
    fs = FailSafeAgent(agent) if not isinstance(agent, FailSafeAgent) else agent
    env.run([fs, opponent])

    per_step = defaultdict(list)
    daily = []
    events = []
    last_day = -1
    cum = {0: Counter(), 1: Counter()}
    latest = {0: None, 1: None}  # (money, melon_shed, shed_total, farm, obs) per player

    for t, step in enumerate(env.steps):
        for p in (0, 1):
            obs = step[p].observation
            act = step[p].action
            farm = obs["farms"][p]
            priv = obs.get("private", {}) or {}
            money = float(farm["money"])
            melon_tiles = _count_melon_tiles(farm)
            melon_shed = int((priv.get("shed", {}) or {}).get("MELON", 0))
            shed_total = sum(int(v) for v in (priv.get("shed", {}) or {}).values()
                            if isinstance(v, (int, float)))
            per_step[f"p{p}_money"].append(money)
            per_step[f"p{p}_melon_tiles"].append(melon_tiles)
            per_step[f"p{p}_melon_shed"].append(melon_shed)
            per_step[f"p{p}_shed_total"].append(shed_total)
            day = obs.get("day", 0)
            hour = obs.get("hour", 0)
            _parse_actions(act or {}, p, day, hour, t, events)
            cum[p]["PLANT_MELON"] += sum(
                1 for ev in events if ev["player"] == p and ev["type"] == "PLANT_MELON" and ev["step"] == t)
            cum[p]["SELL"] += sum(
                1 for ev in events if ev["player"] == p and ev["type"] == "SELL" and ev["step"] == t)
            cum[p]["FERTILIZE"] += sum(
                1 for ev in events if ev["player"] == p and ev["type"] == "FERTILIZE" and ev["step"] == t)
            cum[p]["BUY_FERTILIZER"] += sum(
                1 for ev in events if ev["player"] == p and ev["type"] == "BUY_FERTILIZER" and ev["step"] == t)
            latest[p] = (money, melon_shed, shed_total, farm, obs)
        # Build daily snapshot once both players are captured this step.
        if latest[0] is not None and latest[1] is not None:
            day = latest[0][4].get("day", 0)
            hour = latest[0][4].get("hour", 0)
            if hour == 0 and day != last_day:
                last_day = day
                m0, ms0, st0, farm0, obs0 = latest[0]
                m1, ms1, st1, farm1, obs1 = latest[1]
                market = obs0.get("market", {})
                town = obs0.get("town", {})
                priv1 = obs1.get("private", {}) or {}
                melon_sell_day = sum(ev["n"] for ev in events
                                    if ev["player"] == 0 and ev["type"] == "SELL"
                                    and ev["item"] == "MELON" and ev["day"] == day)
                sell_day = sum(ev["n"] for ev in events
                               if ev["player"] == 0 and ev["type"] == "SELL" and ev["day"] == day)
                opp_melon_sell_day = sum(ev["n"] for ev in events
                                        if ev["player"] == 1 and ev["type"] == "SELL"
                                        and ev["item"] == "MELON" and ev["day"] == day)
                daily.append({
                    "day": day,
                    "p0_money": m0,
                    "p1_money": m1,
                    "margin": m0 - m1,
                    "p0_melon_tiles": _count_melon_tiles(farm0),
                    "p0_melon_shed": ms0,
                    "p0_shed_total": st0,
                    "p0_melon_sell_day": melon_sell_day,
                    "p0_sell_day": sell_day,
                    "p1_melon_shed": int((priv1.get("shed", {}) or {}).get("MELON", 0)),
                    "p1_melon_sell_day": opp_melon_sell_day,
                    "market_melon_price": market.get("prices", {}).get("MELON"),
                    "p0_land": len(farm0.get("unlocked_quadrants", [])),
                    "p0_workers": 1 + len(farm0.get("hands", [])),
                    "p0_animals": _count_animals(farm0),
                    "p0_fertilize_total": cum[0]["FERTILIZE"],
                    "town_shops": list(town.get("unlocked_shops", [])),
                })

    final = env.steps[-1]
    champ_coins = float(final[0].reward if final[0].reward is not None else final[0].observation["farms"][0]["money"])
    market_coins = float(final[1].reward if final[1].reward is not None else final[1].observation["farms"][0]["money"])
    winner = 0 if champ_coins > market_coins else (1 if market_coins > champ_coins else -1)
    fallbacks = fs._stats.get("fallback", 0) if hasattr(fs, "_stats") else 0

    # crop planted counts (from plant events)
    planted = Counter()
    for ev in events:
        if ev["type"] == "PLANT_MELON" and ev["player"] == 0:
            planted["MELON"] += 1

    # melon sold (champion) from SELL events
    melon_sold = sum(ev["n"] for ev in events if ev["player"] == 0 and ev["type"] == "SELL" and ev["item"] == "MELON")
    total_sold = sum(ev["n"] for ev in events if ev["player"] == 0 and ev["type"] == "SELL")

    # endgame days 24-30 window per-step margin + inventory
    endgame = {}
    for d in (24, 25, 26, 27, 28, 29, 30):
        # find last daily entry with day <= d
        snap = None
        for dd in daily:
            if dd["day"] <= d:
                snap = dd
        if snap is not None:
            endgame[str(d)] = {
                "margin": snap["margin"],
                "p0_money": snap["p0_money"],
                "p0_melon_shed": snap["p0_melon_shed"],
                "p0_shed_total": snap["p0_shed_total"],
                "market_melon_price": snap["market_melon_price"],
            }

    return {
        "label": label,
        "seed": seed,
        "winner": winner,
        "champ_coins": champ_coins,
        "market_coins": market_coins,
        "margin": champ_coins - market_coins,
        "fallbacks": fallbacks,
        "planted": dict(planted),
        "melon_sold": melon_sold,
        "total_sold": total_sold,
        "fertilize_count": cum[0]["FERTILIZE"],
        "buy_fertilizer_count": cum[0]["BUY_FERTILIZER"],
        "land": daily[-1]["p0_land"] if daily else 1,
        "workers_end": daily[-1]["p0_workers"] if daily else 1,
        "animals_end": daily[-1]["p0_animals"] if daily else 0,
        "endgame": endgame,
        "daily": daily,
        "per_step": {k: v for k, v in per_step.items()},
        "events": events,
    }


def summarize(games: list[dict], label: str) -> dict:
    wins = sum(1 for g in games if g["winner"] == 0)
    losses = sum(1 for g in games if g["winner"] == 1)
    ties = sum(1 for g in games if g["winner"] == -1)
    coins = [g["champ_coins"] for g in games]
    margins = [g["margin"] for g in games]
    days = list(range(24, 31))
    day28_margins = [g["endgame"].get("28", {}).get("margin") for g in games]
    return {
        "label": label,
        "games": len(games),
        "wins": wins, "losses": losses, "ties": ties,
        "win_rate": wins / len(games),
        "avg_coins": statistics.mean(coins),
        "median_coins": statistics.median(coins),
        "min_coins": min(coins),
        "max_coins": max(coins),
        "avg_margin": statistics.mean(margins),
        "median_margin": statistics.median(margins),
        "avg_melon_sold": statistics.mean([g["melon_sold"] for g in games]),
        "avg_melon_inventory_day28": statistics.mean(
            [g["endgame"].get("28", {}).get("p0_melon_shed", 0) for g in games]),
        "avg_fertilize": statistics.mean([g["fertilize_count"] for g in games]),
        "avg_day28_margin": statistics.mean([m for m in day28_margins if m is not None]),
        "avg_final_margin": statistics.mean(margins),
        "total_fallbacks": sum(g["fallbacks"] for g in games),
    }


def main_cli() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    TEL.mkdir(parents=True, exist_ok=True)

    champion_cfg = FailSafeAgent(make_runtime_agent(ChampionPolicy()))
    champ_games = []
    for seed in SEEDS:
        g = run_game(champion_cfg, seed, "champion")
        (TEL / "champion").mkdir(exist_ok=True)
        (TEL / "champion" / f"seed_{seed:03d}.json").write_text(json.dumps(g, separators=(",", ":")))
        champ_games.append(g)
        print(f"champion  seed {seed:2d}: {g['champ_coins']:.0f} vs {g['market_coins']:.0f} "
              f"{'WIN' if g['winner']==0 else ('loss' if g['winner']==1 else 'TIE')}", flush=True)

    champ_summary = summarize(champ_games, "champion")

    sweep_results = {}
    all_games = {"champion": champ_games}
    for cfg_name, kwargs in CHALLENGER_SWEEP:
        agent = FailSafeAgent(make_runtime_agent(HMarket1Policy(**kwargs)))
        games = []
        for seed in SEEDS:
            g = run_game(agent, seed, cfg_name)
            (TEL / cfg_name).mkdir(exist_ok=True)
            (TEL / cfg_name / f"seed_{seed:03d}.json").write_text(json.dumps(g, separators=(",", ":")))
            games.append(g)
            print(f"{cfg_name:12s} seed {seed:2d}: {g['champ_coins']:.0f} vs {g['market_coins']:.0f} "
                  f"{'WIN' if g['winner']==0 else ('loss' if g['winner']==1 else 'TIE')}", flush=True)
        all_games[cfg_name] = games
        sweep_results[cfg_name] = summarize(games, cfg_name)

    # Select H-MARKET-1 = best by (win_rate, then avg_coins) over the sweep.
    def score(s):
        return (s["wins"], s["avg_coins"])
    best = max(CHALLENGER_SWEEP, key=lambda kv: score(sweep_results[kv[0]]))
    best_name, best_kwargs = best
    hm_games = all_games[best_name]
    hm_summary = sweep_results[best_name]

    # Paired seed-by-seed comparison.
    paired = []
    for i, seed in enumerate(SEEDS):
        cg = champ_games[i]
        hg = hm_games[i]
        paired.append({
            "seed": seed,
            "champion_coins": cg["champ_coins"],
            "challenger_coins": hg["champ_coins"],
            "champion_result": "WIN" if cg["winner"] == 0 else ("loss" if cg["winner"] == 1 else "TIE"),
            "challenger_result": "WIN" if hg["winner"] == 0 else ("loss" if hg["winner"] == 1 else "TIE"),
            "melon_delta": hg["melon_sold"] - cg["melon_sold"],
            "final_margin_delta": hg["margin"] - cg["margin"],
            "champion_margin": cg["margin"],
            "challenger_margin": hg["margin"],
        })

    # Day-28 swing analysis.
    day28 = []
    for i, seed in enumerate(SEEDS):
        cg = champ_games[i]
        hg = hm_games[i]
        day28.append({
            "seed": seed,
            "champion_d28_margin": cg["endgame"].get("28", {}).get("margin"),
            "challenger_d28_margin": hg["endgame"].get("28", {}).get("margin"),
            "champion_final_margin": cg["margin"],
            "challenger_final_margin": hg["margin"],
        })

    results = {
        "experiment": "H-MARKET-1",
        "opponent": "market",
        "seeds": SEEDS,
        "champion_summary": champ_summary,
        "hmarket1_name": best_name,
        "hmarket1_kwargs": best_kwargs,
        "hmarket1_summary": hm_summary,
        "sweep_summaries": sweep_results,
        "paired": paired,
        "day28_swing": day28,
    }
    (ART / "benchmark_results.json").write_text(json.dumps(results, indent=2))

    # config.json
    cfg = {
        "experiment": "H-MARKET-1",
        "opponent": "market",
        "seeds": SEEDS,
        "frozen_baseline": "champion-v1.1 (ChampionPolicy)",
        "selected_hmarket1": {"name": best_name, "kwargs": best_kwargs},
        "sweep_configs": {n: kw for n, kw in CHALLENGER_SWEEP},
        "melon_profiles": {
            "baseline": {"melon_max_tiles": 8, "melon_start_day": 6, "melon_opp_gate": 3,
                          "melon_sell_cap": 3, "sell_min_ratio": 0.85, "endgame_sell_day": 26},
            "low": {"melon_max_tiles": 12, "melon_start_day": 5, "melon_opp_gate": 8,
                    "melon_sell_cap": 4, "sell_min_ratio": 0.80, "endgame_sell_day": 26},
            "medium": {"melon_max_tiles": 16, "melon_start_day": 4, "melon_opp_gate": 99,
                       "melon_sell_cap": 5, "sell_min_ratio": 0.75, "endgame_sell_day": 25},
            "high": {"melon_max_tiles": 20, "melon_start_day": 3, "melon_opp_gate": 99,
                     "melon_sell_cap": 6, "sell_min_ratio": 0.70, "endgame_sell_day": 24},
        },
        "fertilizer_modes": {
            "off": {"enable_fertilizer": False},
            "melon": {"enable_fertilizer": True, "fertilizer_target_crop": "MELON", "fertilizer_buy_threshold": 2},
            "aggressive": {"enable_fertilizer": True, "fertilizer_target_crop": "MELON", "fertilizer_buy_threshold": 4},
        },
    }
    (ART / "config.json").write_text(json.dumps(cfg, indent=2))

    print("\n=== SWEEP SUMMARY ===")
    for n, s in sweep_results.items():
        print(f"{n:12s} W={s['wins']} L={s['losses']} WR={s['win_rate']:.2f} "
              f"avg={s['avg_coins']:.0f} avgMelon={s['avg_melon_sold']:.0f}")
    print(f"SELECTED H-MARKET-1: {best_name} {best_kwargs}")
    print(f"champion avg={champ_summary['avg_coins']:.0f} WR={champ_summary['win_rate']:.2f} "
          f"| hmarket1 avg={hm_summary['avg_coins']:.0f} WR={hm_summary['win_rate']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_cli())
