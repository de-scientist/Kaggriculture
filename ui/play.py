import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent import agent
from kaggle_environments import make

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]

def synth_decision(turn_action, obs):
    fa = turn_action.get("farmer", ["PASS"])
    op = fa[0] if fa else "PASS"
    market_ops = turn_action.get("market", [])
    kind = "wait"
    summary = "Observed the board and held position."
    if any(m and m[0] == "SELL" for m in market_ops):
        kind = "trade"
        qty = sum(int(m[2]) for m in market_ops if m and m[0] == "SELL")
        summary = f"Sold {qty} units on the market."
    elif op == "PLANT":
        kind = "farm"; summary = f"Planted {fa[1] if len(fa) > 1 else 'a crop'}."
    elif op == "WATER":
        kind = "farm"; summary = "Watered the current tile."
    elif op == "HARVEST":
        kind = "farm"; summary = "Harvested the current tile."
    elif op == "FERTILIZE":
        kind = "farm"; summary = "Fertilized the current tile."
    elif op == "FEED":
        kind = "farm"; summary = "Fed animals."
    elif op == "BUILD_COOP" or op == "BUILD_PASTURE":
        kind = "expand"; summary = "Built an animal structure."
    elif op == "BUY_LAND":
        kind = "expand"; summary = "Bought new land."
    elif op == "DIG":
        kind = "farm"; summary = "Cleared the current tile."
    day = obs.get("day", 0)
    if day < 5: mode = "STARTUP"
    elif day < 12: mode = "GROWTH"
    elif day < 22: mode = "PRODUCTION"
    elif day < 26: mode = "EXPANSION"
    else: mode = "ENDGAME"
    best = max(obs.get("market", {}).get("prices", {}).items(), key=lambda kv: kv[1], default=("WHEAT", 0))
    factors = [
        f"Top price: {best[0]} at {best[1]}c.",
        f"Cash on hand: {obs.get('farms', [{}])[0].get('money', 0)}c.",
        f"Day {day + 1}/30 — {mode.lower()} phase.",
    ]
    return {
        "type": kind,
        "summary": summary,
        "expected_value": 0,
        "strategy_mode": mode,
        "confidence": {"value": 0.85, "level": "High"},
        "factors": factors,
        "policy": "champion",
        "n_candidates": 0,
        "alternatives": [],
    }

def run(opponent, seed, steps, version, agent_name="ours"):
    players = [agent, opponent] if agent_name == "ours" else [agent_name, opponent]
    env = make("kaggriculture", configuration={"episodeSteps": steps, "seed": seed})
    env.run(players)
    data = env.toJSON()
    steps_list = data["steps"]
    rewards = data.get("rewards", [None, None])

    turns = []
    for i, frame in enumerate(steps_list):
        entry = frame[0]
        obs = entry.get("observation")
        if not obs or "farms" not in obs:
            continue
        p0 = obs["farms"][0]
        p1 = obs["farms"][1] if len(obs["farms"]) > 1 else {"money": 0}
        action = entry.get("action", {"farmer": ["PASS"], "hands": [], "market": []})
        decision = synth_decision(action, obs)
        turns.append({
            "turn": i,
            "day": obs.get("day", 0),
            "hour": obs.get("hour", 0),
            "money": p0.get("money", 0),
            "opp_money": p1.get("money", 0),
            "farm": p0,
            "private": obs.get("private", {"shed": {}, "seeds": {}, "inventories": []}),
            "market": obs.get("market", {"inventory": {}, "prices": {}}),
            "town": obs.get("town", {"unlocked_shops": []}),
            "action": action,
            "opp_action": frame[1].get("action") if len(frame) > 1 else None,
            "decision": decision,
        })

    money_history = [t["money"] for t in turns]
    opp_money_history = [t["opp_money"] for t in turns]
    price_history = {p: [t["market"]["prices"].get(p, 0) for t in turns] for p in PRODUCTS}
    actions_log = [
        {"turn": t["turn"], "day": t["day"], "hour": t["hour"], "action": t["action"], "decision": t["decision"]}
        for t in turns
    ]
    final = {
        "money": money_history[-1] if money_history else 0,
        "opp_money": opp_money_history[-1] if opp_money_history else 0,
        "reward": rewards[0],
        "status": "DONE",
    }
    game = {
        "id": f"played-{version}-vs-{opponent}-s{seed}",
        "agent_version": version,
        "opponent": opponent,
        "seed": seed,
        "episode_steps": steps,
        "real": True,
        "turns": turns,
        "money_history": money_history,
        "opp_money_history": opp_money_history,
        "price_history": price_history,
        "actions_log": actions_log,
        "final": final,
    }
    return game

def main():
    ap = argparse.ArgumentParser(description="Run the Kaggriculture agent and export a replay for the UI.")
    ap.add_argument("--opponent", default="random")
    ap.add_argument("--agent", default="ours", help="ours | starter | random | pass")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("--version", default="v1.2")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data", "played.json"))
    args = ap.parse_args()

    existing = None
    games_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data", "games.json")
    if os.path.exists(games_path):
        try:
            existing = json.load(open(games_path))
        except Exception:
            existing = None

    version = args.version if args.agent == "ours" else args.agent
    game = run(args.opponent, args.seed, args.steps, version, args.agent)

    dataset = {
        "generated_at": "",
        "source": "played",
        "games": [game],
        "championship": (existing or {}).get("championship", {"source": "none", "data": None}),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(dataset, open(args.out, "w"))
    print(f"Wrote replay -> {args.out}")
    print(f"  agent {args.version} vs {args.opponent} (seed {args.seed}), {len(game['turns'])} turns")
    print(f"  final coins: {game['final']['money']}  opponent: {game['final']['opp_money']}  reward: {game['final']['reward']}")

if __name__ == "__main__":
    main()
