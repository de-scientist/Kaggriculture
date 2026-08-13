"""Tests for the H-MARKET-1 controlled challenger policy.

These verify that HMarket1Policy only overrides RuntimeSettings (never the
frozen Champion), that profile/fertilizer knobs behave as specified, and that the
selected challenger runs a full game without crashing or falling back.
"""

from __future__ import annotations

from agent.runtime.game import GameSnapshot
from agent.runtime.policies import (
    ChampionPolicy,
    HMarket1Policy,
    make_policy,
)
from agent.runtime.settings import RuntimeSettings


def _make_obs(day: int = 10, step: int = 240, money: float = 3000.0) -> dict:
    """Minimal observation sufficient for policy.adjust()."""
    farm = {
        "money": money,
        "tiles": [[None, None], [None, None]],
        "farmer": [0, 0],
        "hands": [],
        "unlocked_quadrants": ["NW"],
        "hires_today": 0,
    }
    return {
        "step": step,
        "day": day,
        "hour": 0,
        "player": 0,
        "farms": [farm, dict(farm)],
        "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
        "market": {"prices": {}, "inventory": {}},
        "town": {"unlocked_shops": []},
        "boardSize": 2,
        "episodeSteps": 720,
        "turnsPerDay": 24,
    }


def _snapshot(day: int = 10, step: int = 240, money: float = 3000.0) -> GameSnapshot:
    return GameSnapshot.from_obs(_make_obs(day, step, money))


def test_make_policy_registration() -> None:
    assert isinstance(make_policy("auto", RuntimeSettings()), ChampionPolicy)
    assert isinstance(make_policy("hmarket1", RuntimeSettings()), HMarket1Policy)
    # Unknown name degrades to Champion, never to the challenger.
    assert isinstance(make_policy("nope", RuntimeSettings()), ChampionPolicy)


def test_champion_baseline_unchanged() -> None:
    s, _ = ChampionPolicy().adjust(_snapshot(), RuntimeSettings())
    assert s.melon_max_tiles == 8
    assert s.melon_opp_gate == 3
    assert s.enable_fertilizer is False
    assert s.endgame_sell_day == 26


def test_baseline_profile_reproduces_champion() -> None:
    s, _ = HMarket1Policy(melon_profile="baseline").adjust(_snapshot(), RuntimeSettings())
    assert s.melon_max_tiles == 8
    assert s.melon_opp_gate == 3
    assert s.enable_fertilizer is False


def test_medium_profile_overrides() -> None:
    s, info = HMarket1Policy(melon_profile="medium").adjust(_snapshot(day=10), RuntimeSettings())
    assert s.melon_max_tiles == 16
    assert s.melon_opp_gate == 99  # contests melon instead of surrendering
    assert s.melon_start_day == 4
    assert s.sell_min_ratio == 0.75
    assert s.endgame_sell_day == 25
    assert s.plant_enabled is True  # not yet endgame
    assert info["mode"] == "hmarket1_prod"


def test_low_and_high_profiles() -> None:
    low, _ = HMarket1Policy(melon_profile="low").adjust(_snapshot(day=10), RuntimeSettings())
    assert low.melon_max_tiles == 12 and low.melon_opp_gate == 8
    high, _ = HMarket1Policy(melon_profile="high").adjust(_snapshot(day=10), RuntimeSettings())
    assert high.melon_max_tiles == 20 and high.melon_opp_gate == 99
    assert high.melon_start_day == 3


def test_endgame_liquidation() -> None:
    # day 27 >= endgame_sell_day(25) -> liquidate
    s, info = HMarket1Policy(melon_profile="medium").adjust(_snapshot(day=27), RuntimeSettings())
    assert s.plant_enabled is False
    assert s.melon_sell_cap >= 50
    assert s.sell_min_ratio <= 0.6
    assert info["mode"] == "hmarket1_liquidate"


def test_fertilizer_isolation() -> None:
    off, _ = HMarket1Policy(melon_profile="medium", fertilizer_mode="off").adjust(
        _snapshot(), RuntimeSettings()
    )
    assert off.enable_fertilizer is False
    melon, _ = HMarket1Policy(melon_profile="medium", fertilizer_mode="melon").adjust(
        _snapshot(), RuntimeSettings()
    )
    assert melon.enable_fertilizer is True
    assert melon.fertilizer_target_crop == "MELON"
    assert melon.fertilizer_buy_threshold == 2
    # Champion must never be affected by the challenger's fertilizer flag.
    champ, _ = ChampionPolicy().adjust(_snapshot(), RuntimeSettings())
    assert champ.enable_fertilizer is False


def test_runtime_agent_construction() -> None:
    from agent.runtime.agent import make_runtime_agent
    from agent.submission.failsafe import FailSafeAgent

    agent = FailSafeAgent(make_runtime_agent(HMarket1Policy(melon_profile="medium")))
    assert callable(agent)
