"""Tests for the Stage 4 champion/challenger arena and champion protection."""

from __future__ import annotations

from agent.evaluation.tournament import MatchResult, TournamentResult
from agent.submission.championship import (
    ArenaConfig,
    Candidate,
    ChampionArena,
    default_candidates,
    select_champion_from_tournament,
)


def _result(pairs: list[tuple[str, str, float, float]]) -> TournamentResult:
    return TournamentResult(
        matches=[
            MatchResult(agent_a=a, agent_b=b, reward_a=ra, reward_b=rb, winner=0 if ra > rb else (1 if rb > ra else -1))
            for a, b, ra, rb in pairs
        ]
    )


def test_select_champion_picks_top() -> None:
    arena = ChampionArena(default_candidates())
    res = _result([("champion_endgame", "hybrid", 5000.0, 4000.0)])
    assert arena.select_champion(res) == "champion_endgame"


def test_champion_protection_keeps_incumbent_on_tie() -> None:
    arena = ChampionArena(default_candidates())
    # Incumbent 'hybrid' ties with challenger 'champion_endgame'.
    res = _result([("champion_endgame", "hybrid", 4000.0, 4000.0)])
    assert arena.select_champion(res, current_champion="hybrid") == "hybrid"


def test_champion_protection_dethroned_only_on_clear_win() -> None:
    arena = ChampionArena(default_candidates(), ArenaConfig(win_margin=200.0))
    # Challenger wins by a small margin -> incumbent kept.
    res = _result([("champion_endgame", "hybrid", 4100.0, 4000.0)])
    assert arena.select_champion(res, current_champion="hybrid") == "hybrid"
    # Challenger wins by a clear margin -> dethroned.
    res2 = _result([("champion_endgame", "hybrid", 4500.0, 4000.0)])
    assert arena.select_champion(res2, current_champion="hybrid") == "champion_endgame"


def test_default_candidates_build_agents() -> None:
    for cand in default_candidates():
        agent_fn = cand.build()
        assert callable(agent_fn)


def test_select_champion_from_tournament_helper() -> None:
    res = _result([("champion_endgame", "hybrid", 5000.0, 4000.0)])
    assert select_champion_from_tournament(res, default_candidates()) == "champion_endgame"
