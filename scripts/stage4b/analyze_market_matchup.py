"""Stage 4B — analyse MARKET_MATCHUP telemetry and emit findings JSON.

Reads artifacts/championship/MARKET_MATCHUP_TELEMETRY/seed_NNN.json and
artifacts/championship/MARKET_MATCHUP_RESULTS.json, computes win/loss
characteristics, turning points, and inventory/liquidation behaviour, and writes
artifacts/championship/MARKET_MATCHUP_FINDINGS.json (pure computed evidence, no
causal claims).
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ART = Path("artifacts/championship")
TEL = ART / "MARKET_MATCHUP_TELEMETRY"

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]


def load_games():
    games = []
    for p in sorted(TEL.glob("seed_*.json")):
        games.append(json.loads(p.read_text()))
    return games


def daily_margin(g):
    return [d["p0_money"] - d["p1_money"] for d in g["daily"]]


def turning_point(g):
    """Day the eventual winner's lead becomes durable (sign of margin stops flipping)."""
    dm = daily_margin(g)
    final_sign = 1 if g["margin"] >= 0 else -1
    # last day where margin sign differs from final sign
    last_flip = -1
    for i, m in enumerate(dm):
        if m == 0:
            continue
        if (m > 0) != (final_sign > 0):
            last_flip = i
    established_day = last_flip + 1 if last_flip >= 0 else 0
    # peak advantage day for eventual winner
    if final_sign > 0:
        peak_day = max(range(len(dm)), key=lambda i: dm[i])
    else:
        peak_day = min(range(len(dm)), key=lambda i: dm[i])
    return {
        "established_day": established_day,
        "margin_at_established": dm[established_day] if 0 <= established_day < len(dm) else None,
        "peak_day": peak_day,
        "peak_margin": dm[peak_day],
        "final_margin": g["margin"],
    }


def total_sold_units(g, player, min_day=0):
    tot = 0
    for e in g["events"]:
        if e["player"] != player or e["type"] != "SELL":
            continue
        if e["day"] < min_day:
            continue
        tot += e["detail"]["n"] or 0
    return tot


def total_sell_events(g, player, min_day=0):
    return sum(1 for e in g["events"]
               if e["player"] == player and e["type"] == "SELL" and e["day"] >= min_day)


def sold_by_product(g, player):
    """Units sold per product from SELL events."""
    out = Counter()
    for e in g["events"]:
        if e["player"] != player or e["type"] != "SELL":
            continue
        out[e["detail"]["item"]] += e["detail"]["n"] or 0
    return out


def estimated_revenue(g, player):
    """Approximate gross revenue from SELL events using the day's market price.

    This is an estimate (assumes the sale clears at that day's shared market
    price); it is correlation-grade evidence, not an exact accounting.
    """
    total = 0.0
    by_product = Counter()
    price_at_sale = []
    for e in g["events"]:
        if e["player"] != player or e["type"] != "SELL":
            continue
        item = e["detail"]["item"]
        n = e["detail"]["n"] or 0
        day = e["day"]
        price = None
        for d in g["daily"]:
            if d["day"] == day:
                price = d["market_prices"].get(item)
                break
        if price is None:
            continue
        rev = n * price
        total += rev
        by_product[item] += rev
        price_at_sale.append(price)
    return total, by_product, (statistics.mean(price_at_sale) if price_at_sale else None)


def main():
    games = load_games()
    wins = [g for g in games if g["winner"] == 0]
    losses = [g for g in games if g["winner"] == 1]

    def final_metric(g, key):
        return g["daily"][-1].get(key)

    def avg_group(grp, fn):
        return statistics.mean(fn(g) for g in grp) if grp else float("nan")

    # Per-group characteristics.
    def characterize(grp):
        out = {}
        out["n"] = len(grp)
        out["avg_champ_coins"] = avg_group(grp, lambda g: g["champ_coins"])
        out["avg_market_coins"] = avg_group(grp, lambda g: g["market_coins"])
        out["avg_margin"] = avg_group(grp, lambda g: g["margin"])
        out["avg_final_land"] = avg_group(grp, lambda g: final_metric(g, "p0_land"))
        out["avg_final_animals"] = avg_group(grp, lambda g: final_metric(g, "p0_animals"))
        out["avg_final_planted"] = avg_group(grp, lambda g: final_metric(g, "p0_planted"))
        # workers: average over last 5 days (per-day active hands+1)
        out["avg_final_workers"] = avg_group(
            grp, lambda g: statistics.mean(d["p0_workers"] for d in g["daily"][-5:]))
        # shed carry: average over last 5 days
        out["avg_late_shed"] = avg_group(
            grp, lambda g: statistics.mean(d["p0_shed_total"] for d in g["daily"][-5:]))
        out["avg_final_shed"] = avg_group(grp, lambda g: final_metric(g, "p0_shed_total"))
        out["total_sold_units"] = sum(total_sold_units(g, 0) for g in grp)
        out["total_endgame_sold_units"] = sum(total_sold_units(g, 0, min_day=26) for g in grp)
        out["avg_endgame_sold_units"] = avg_group(grp, lambda g: total_sold_units(g, 0, min_day=26))
        out["avg_total_sold_units"] = avg_group(grp, lambda g: total_sold_units(g, 0))
        out["total_buy_land"] = sum(g["cum_events"]["0"].get("BUY_LAND", 0) for g in grp)
        out["total_hire"] = sum(g["cum_events"]["0"].get("HIRE", 0) for g in grp)
        out["total_fertilize"] = sum(g["cum_events"]["0"].get("FERTILIZE", 0) for g in grp)
        return out

    win_char = characterize(wins)
    loss_char = characterize(losses)

    # Market opponent perspective (player 1) in win vs loss games.
    def market_char(grp):
        return {
            "avg_final_land": avg_group(grp, lambda g: final_metric(g, "p1_land")),
            "avg_final_animals": avg_group(grp, lambda g: final_metric(g, "p1_animals")),
            "avg_final_planted": avg_group(grp, lambda g: final_metric(g, "p1_planted")),
            "avg_late_shed": avg_group(grp, lambda g: statistics.mean(d["p1_shed_total"] for d in g["daily"][-5:])),
            "avg_total_sold_units": avg_group(grp, lambda g: total_sold_units(g, 1)),
            "avg_endgame_sold_units": avg_group(grp, lambda g: total_sold_units(g, 1, min_day=26)),
        }
    market_in_win = market_char(wins)
    market_in_loss = market_char(losses)

    # Turning points.
    tps = {g["seed"]: turning_point(g) for g in games}

    # Early-game margin trajectory (day 0..10) to see who leads early.
    early_lead = {}
    for g in games:
        early = daily_margin(g)[:11]
        early_lead[g["seed"]] = {
            "day0_margin": daily_margin(g)[0] if daily_margin(g) else None,
            "day5_margin": daily_margin(g)[5] if len(daily_margin(g)) > 5 else None,
            "day10_margin": daily_margin(g)[10] if len(daily_margin(g)) > 10 else None,
            "winner": g["winner"],
        }

    # Shed carry comparison: champion late-shed in win vs loss (unsold inventory
    # at end does NOT count toward coins).

    # Product-level sales + estimated revenue (the key differentiator hypothesis).
    champ_sold_win = Counter()
    champ_sold_loss = Counter()
    mkt_sold_win = Counter()
    mkt_sold_loss = Counter()
    champ_rev_win = 0.0
    champ_rev_loss = 0.0
    mkt_rev_win = 0.0
    mkt_rev_loss = 0.0
    for g in wins:
        champ_sold_win += sold_by_product(g, 0)
        mkt_sold_win += sold_by_product(g, 1)
        cr, _, _ = estimated_revenue(g, 0)
        mr, _, _ = estimated_revenue(g, 1)
        champ_rev_win += cr
        mkt_rev_win += mr
    for g in losses:
        champ_sold_loss += sold_by_product(g, 0)
        mkt_sold_loss += sold_by_product(g, 1)
        cr, _, _ = estimated_revenue(g, 0)
        mr, _, _ = estimated_revenue(g, 1)
        champ_rev_loss += cr
        mkt_rev_loss += mr

    # Crop mix the champion carries (final day shed + planted crop_by).
    def crop_mix(grp):
        planted = Counter()
        shed = Counter()
        for g in grp:
            last = g["daily"][-1]
            for c, n in last.get("p0_crop_by", {}).items():
                planted[c] += n
            for c, n in last.get("p0_shed", {}).items():
                if c in PRODUCTS:
                    shed[c] += n
        return dict(planted), dict(shed)

    win_planted, win_shed = crop_mix(wins)
    loss_planted, loss_shed = crop_mix(losses)

    findings = {
        "win_characteristics": win_char,
        "loss_characteristics": loss_char,
        "market_in_win_games": market_in_win,
        "market_in_loss_games": market_in_loss,
        "turning_points": tps,
        "early_lead": early_lead,
        "product_sales": {
            "champion_in_wins_by_product": dict(champ_sold_win),
            "champion_in_losses_by_product": dict(champ_sold_loss),
            "market_in_wins_by_product": dict(mkt_sold_win),
            "market_in_losses_by_product": dict(mkt_sold_loss),
        },
        "estimated_revenue": {
            "champion_in_wins": champ_rev_win,
            "champion_in_losses": champ_rev_loss,
            "market_in_wins": mkt_rev_win,
            "market_in_losses": mkt_rev_loss,
        },
        "crop_mix": {
            "win_planted": win_planted, "win_shed": win_shed,
            "loss_planted": loss_planted, "loss_shed": loss_shed,
        },
        "summary_counts": {
            "games": len(games), "wins": len(wins), "losses": len(losses),
        },
    }
    (ART / "MARKET_MATCHUP_FINDINGS.json").write_text(json.dumps(findings, indent=2))

    # Console summary.
    print("=== WIN games champion characteristics ===")
    for k, v in win_char.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
    print("=== LOSS games champion characteristics ===")
    for k, v in loss_char.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
    print("=== MARKET opponent in WIN games (champ perspective) ===", market_in_win)
    print("=== MARKET opponent in LOSS games ===", market_in_loss)
    print("=== Turning points (established day, peak day) ===")
    for s, tp in sorted(tps.items()):
        print(f"  seed {s}: est_day={tp['established_day']} est_margin={tp['margin_at_established']} "
              f"peak_day={tp['peak_day']} peak_margin={tp['peak_margin']} final={tp['final_margin']:.0f}")
    return findings


if __name__ == "__main__":
    main()
