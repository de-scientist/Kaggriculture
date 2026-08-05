import pytest
from kaggriculture_ai.domain.entities import GameState, Turn, Season, Farm


def test_turn_creation():
    turn = Turn(day=0, hour=0, step=0)
    assert turn.day == 0
    assert turn.hour == 0
    assert turn.step == 0


def test_season_creation():
    season = Season(turn_count=0, turns_per_day=24, days=30)
    assert season.current_day == 0


def test_farm_creation():
    farm = Farm(owner=0, board_size=10)
    assert farm.owner == 0
    assert farm.board_size == 10