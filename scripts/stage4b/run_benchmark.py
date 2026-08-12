"""Stage 4B benchmark driver.

Runs the Champion baseline, the EndgamePolicy ablation, and a set of controlled
challengers through the :mod:`agent.evaluation.benchmark_runner`, persisting
every match incrementally to ``artifacts/championship/CHAMPION_TOURNAMENT_RESULTS.json``.

Usage:
    python scripts/stage4b/run_benchmark.py [--seeds 3] [--baseline-seeds 3] [--challenger-seeds 2]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Allow running as a script from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agent.evaluation.benchmark_runner import BenchmarkRunner, MetricsAgent  # noqa: E402
from agent.evaluation.metrics import BenchmarkSummary, MatchMetrics  # noqa: E402
from agent.evaluation.opponents import build_opponent  # noqa: E402
from agent.evaluation.registry import (  # noqa: E402
    Challenger,
    ChallengerRegistry,
    ChampionRegistry,
    ChampionVersion,
    Hypothesis,
    HypothesisRegistry,
)
from agent.evaluation.reporter import (  # noqa: E402
    tournament_report_markdown,
    write_tournament_results,
)
from agent.runtime.agent import make_runtime_agent  # noqa: E402
from agent.runtime.policies import ChampionPolicy, EndgamePolicy  # noqa: E402
from agent.runtime.settings import RuntimeSettings  # noqa: E402
from agent.submission.failsafe import FailSafeAgent  # noqa: E402
import main  # noqa: E402

ART = Path("artifacts/championship")
BASELINE_OPPONENTS = ["random", "starter", "conservative", "aggressive", "expansion", "production", "market"]
CHALLENGER_OPPONENTS = ["champion", "starter", "conservative", "aggressive"]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def champion_agent() -> Any:
    return FailSafeAgent(make_runtime_agent("auto"))


def save_incremental(matches: list[MatchMetrics]) -> None:
    write_tournament_results(matches, ART / "CHAMPION_TOURNAMENT_RESULTS.json")


def run_suite(
    our_agent: Any,
    our_name: str,
    opponents: dict[str, Any],
    seeds: tuple[int, ...],
    all_matches: list[MatchMetrics],
) -> None:
    runner = BenchmarkRunner(
        our_agent=our_agent,
        opponents=opponents,
        seeds=seeds,
        candidate_name=our_name,
    )
    for opp_name, opp in opponents.items():
        for seed in seeds:
            try:
                m = runner.run_match(opp_name, opp, seed)
            except Exception as exc:  # noqa: BLE001
                sys.stderr.write(f"ERROR {our_name} vs {opp_name} s{seed}: {exc}\n")
                continue
            all_matches.append(m)
            save_incremental(all_matches)
            sys.stderr.write(
                f"{our_name} vs {opp_name} s{seed}: "
                f"coins={m.our_final_coins:.0f} opp={m.opponent_final_coins:.0f} "
                f"w={m.winner} fb={m.fallback_count}\n"
            )


def main_cli() -> int:  # pragma: no cover - manual entry point
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--baseline-seeds", type=int, default=3)
    ap.add_argument("--challenger-seeds", type=int, default=2)
    args = ap.parse_args()

    ART.mkdir(parents=True, exist_ok=True)
    commit = git_commit()
    all_matches: list[MatchMetrics] = []

    # --- Champion baseline -------------------------------------------------
    champ = champion_agent()
    baseline_opps = {o: build_opponent(o) for o in BASELINE_OPPONENTS}
    baseline_opps["champion"] = FailSafeAgent(make_runtime_agent("auto"))  # self-play reference
    run_suite(champ, "champion-v1.0", baseline_opps, tuple(range(args.baseline_seeds)), all_matches)

    # --- EndgamePolicy ablation ------------------------------------------
    no_endgame = FailSafeAgent(make_runtime_agent(ChampionPolicy()))
    run_suite(
        champ,
        "champion-v1.0",
        {"no_endgame": no_endgame},
        tuple(range(args.seeds)),
        all_matches,
    )

    # --- Challengers ------------------------------------------------------
    challengers = {
        "C01": Challenger(
            candidate_id="C01",
            parent="champion-v1.0",
            version="c01",
            hypothesis="Higher cash reserve + fewer workers reduces ruin risk and improves robustness (H: capital discipline).",
            commit=commit,
            configuration={"reserve_money": 600, "target_hands": (2, 2, 3, 3), "land_budget_ratio": 4.0, "melon_max_tiles": 4, "enable_animals": False},
            changed_params=["reserve_money", "target_hands", "land_budget_ratio", "melon_max_tiles", "enable_animals"],
            expected_outcome="More robust, possibly lower peak coins.",
        ),
        "C02": Challenger(
            candidate_id="C02",
            parent="champion-v1.0",
            version="c02",
            hypothesis="Aggressive early expansion (more workers, animals, melon, early land) yields higher terminal coins.",
            commit=commit,
            configuration={"reserve_money": 80, "target_hands": (5, 6, 7, 8), "land_budget_ratio": 1.2, "enable_animals": True, "cow_max": 4, "goose_max": 2, "melon_max_tiles": 12},
            changed_params=["reserve_money", "target_hands", "land_budget_ratio", "enable_animals", "cow_max", "goose_max", "melon_max_tiles"],
            expected_outcome="Higher average coins if expansion pays off.",
        ),
        "C08": Challenger(
            candidate_id="C08",
            parent="champion-v1.0",
            version="c08",
            hypothesis="Liquidating earlier (endgame_day 24, wind_down_day 20) improves terminal cash vs default 26/22.",
            commit=commit,
            configuration={"policy": "EndgamePolicy(endgame_day=24, wind_down_day=20)"},
            changed_params=["endgame_day", "wind_down_day"],
            expected_outcome="Higher terminal cash if earlier liquidation is beneficial.",
        ),
    }
    chall_reg = ChallengerRegistry()
    for cid, ch in challengers.items():
        if challengers[cid].configuration.get("policy", "").startswith("EndgamePolicy"):
            agent = FailSafeAgent(make_runtime_agent(EndgamePolicy(endgame_day=24, wind_down_day=20)))
        else:
            agent = FailSafeAgent(make_runtime_agent("auto", settings=RuntimeSettings(**ch.configuration)))
        opps = {o: (champ if o == "champion" else build_opponent(o)) for o in CHALLENGER_OPPONENTS}
        run_suite(agent, cid, opps, tuple(range(args.challenger_seeds)), all_matches)
        # record simple summary in the registry
        summary = BenchmarkSummary(candidate=cid, matches=[m for m in all_matches if m.our_agent == cid])
        chall_reg.register(ch)
        chall_reg.record_result(
            cid,
            {
                "games": len(summary.matches),
                "wins": summary.total_wins(),
                "losses": summary.total_losses(),
                "ties": summary.total_ties(),
                "win_rate": summary.overall_win_rate(),
                "avg_coins": summary.avg_coins(),
                "median_coins": summary.median_coins(),
                "best": summary.best_coins(),
                "worst": summary.worst_coins(),
                "avg_decision_ms": summary.avg_decision_ms(),
                "max_decision_ms": summary.max_decision_ms(),
                "fallbacks": summary.total_fallbacks(),
            },
        )

    # --- Registries -------------------------------------------------------
    champ_reg = ChampionRegistry()
    champ_reg.record(
        ChampionVersion(
            version="champion-v1.0",
            commit=commit,
            config={"policy": "EndgamePolicy", "wind_down_day": 22, "endgame_day": 26},
            notes="Stage 4 champion: EndgamePolicy + FailSafeAgent.",
            frozen_at="stage4b",
        )
    )
    hyp_reg = HypothesisRegistry()
    for hid, hyp in [
        ("H-A", "Stopping land expansion late improves final liquidity."),
        ("H-B", "Stopping animal purchases late improves terminal wealth."),
        ("H-C", "Tapering hiring from ~day 22 improves profitability."),
        ("H-D", "Stopping planting from ~day 26 improves terminal cash."),
        ("H-E", "Late inventory liquidation improves final score."),
    ]:
        hyp_reg.add(
            Hypothesis(
                id=hid,
                date="stage4b",
                hypothesis=hyp,
                reason="Endgame optimization",
                affected_component="EndgamePolicy",
                expected_effect="higher terminal cash",
                experiment="ablation vs no_endgame",
            )
        )

    # --- Reports ----------------------------------------------------------
    champ_summary = BenchmarkSummary(candidate="champion-v1.0", matches=[m for m in all_matches if m.our_agent == "champion-v1.0" and m.opponent != "champion"])
    (ART / "CHAMPION_TOURNAMENT_REPORT.md").write_text(
        tournament_report_markdown(champ_summary, "Champion Tournament (Stage 4B)"), encoding="utf-8"
    )
    save_incremental(all_matches)
    print(f"DONE. {len(all_matches)} matches saved to {ART / 'CHAMPION_TOURNAMENT_RESULTS.json'}")
    print(tournament_report_markdown(champ_summary, "Champion Tournament (Stage 4B)"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main_cli())
