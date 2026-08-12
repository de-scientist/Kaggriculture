"""Reporting helpers for Stage 4B benchmark results.

Produces markdown tables for the tournament report and writes the canonical
``CHAMPION_TOURNAMENT_RESULTS.json`` artifact.  All numbers come from measured
:class:`~agent.evaluation.metrics.MatchMetrics`; nothing is fabricated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from agent.evaluation.metrics import BenchmarkSummary, MatchMetrics, OpponentSummary


def _fmt(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}"


def match_table(summary: BenchmarkSummary) -> str:
    by_opp = summary.by_opponent()
    header = (
        "| Opponent | Games | Wins | Losses | Ties | Win Rate | "
        "Avg Coins | Avg Margin |"
    )
    sep = "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    lines = [header, sep]
    for opp in sorted(by_opp):
        s = by_opp[opp]
        lo, hi = s.win_rate_ci95()
        lines.append(
            f"| {opp} | {s.games} | {s.wins} | {s.losses} | {s.ties} | "
            f"{_fmt(s.win_rate * 100, 1)}% ({_fmt(lo*100,0)}-{_fmt(hi*100,0)}) | "
            f"{_fmt(summary_baseline_coins(summary, opp))} | "
            f"{_fmt(_opp_avg_margin(summary, opp))} |"
        )
    return "\n".join(lines)


def _opp_avg_coins(summary: BenchmarkSummary, opp: str) -> float:
    vals = [m.our_final_coins for m in summary.matches if m.opponent == opp]
    return sum(vals) / len(vals) if vals else 0.0


def _opp_avg_margin(summary: BenchmarkSummary, opp: str) -> float:
    vals = [m.coin_margin for m in summary.matches if m.opponent == opp]
    return sum(vals) / len(vals) if vals else 0.0


def summary_baseline_coins(summary: BenchmarkSummary, opp: str) -> float:  # re-exported alias
    return _opp_avg_coins(summary, opp)


def tournament_report_markdown(
    summary: BenchmarkSummary,
    title: str = "Champion Tournament",
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Candidate: **{summary.candidate}**",
        f"- Matches: {len(summary.matches)}",
        f"- Overall win rate: {_fmt(summary.overall_win_rate() * 100, 1)}%",
        f"- Total W/L/T: {summary.total_wins()}/{summary.total_losses()}/{summary.total_ties()}",
        f"- Avg final coins: {_fmt(summary.avg_coins())}",
        f"- Median final coins: {_fmt(summary.median_coins())}",
        f"- Best / worst: {_fmt(summary.best_coins())} / {_fmt(summary.worst_coins())}",
        f"- Avg decision (ms): {_fmt(summary.avg_decision_ms(), 3)}",
        f"- Max decision (ms): {_fmt(summary.max_decision_ms(), 3)}",
        f"- Total fallbacks: {summary.total_fallbacks()}",
        "",
        "## Per-opponent",
        "",
        match_table(summary),
        "",
    ]
    return "\n".join(lines)


def write_tournament_results(matches: Sequence[MatchMetrics], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data: list[dict[str, Any]] = [m.to_dict() for m in matches]
    path.write_text(__import__("json").dumps(data, indent=2), encoding="utf-8")


def load_tournament_results(path: str | Path) -> list[MatchMetrics]:
    import json

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [MatchMetrics(**r) for r in raw]
