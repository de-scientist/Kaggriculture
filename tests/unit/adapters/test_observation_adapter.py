"""Unit tests for the ObservationAdapter (chapter 9)."""
from __future__ import annotations

import pytest

from agent.adapters.observation_adapter import ObservationAdapter
from agent.adapters.validators import validate_observation_not_none
from agent.domain.game_state import GameState

from tests.fixtures.observations import (
    minimal_observation,
    observation_advanced,
    observation_malformed,
    observation_partial,
    observation_with_animal,
    observation_with_crop,
    observation_with_hands,
    observation_with_market,
    observation_with_money,
    observation_with_seeds,
    observation_with_shed,
    observation_with_town,
)


@pytest.fixture
def adapter() -> ObservationAdapter:
    return ObservationAdapter()


class TestObservationAdapterParse:
    def test_parse_minimal_observation(self, adapter: ObservationAdapter) -> None:
        state = adapter.parse(minimal_observation())
        assert isinstance(state, GameState)
        assert state.player == 0
        assert state.current_day() == 0
        assert state.current_turn() == 0

    def test_parse_sets_step(self, adapter: ObservationAdapter) -> None:
        obs = minimal_observation()
        obs["step"] = 42
        state = adapter.parse(obs)
        assert state.step == 42

    def test_parse_sets_money(self, adapter: ObservationAdapter) -> None:
        obs = observation_with_money(5000.0)
        state = adapter.parse(obs)
        assert state.available_money() == 5000.0

    def test_parse_sets_seeds_in_private(self, adapter: ObservationAdapter) -> None:
        obs = observation_with_seeds({"WHEAT": 5, "CARROT": 3})
        state = adapter.parse(obs)
        assert state.private["seeds"] == {"WHEAT": 5, "CARROT": 3}

    def test_parse_sets_shed_in_private(self, adapter: ObservationAdapter) -> None:
        obs = observation_with_shed({"WHEAT": 10})
        state = adapter.parse(obs)
        assert state.private["shed"]["WHEAT"] == 10

    def test_parse_sets_hands(self, adapter: ObservationAdapter) -> None:
        obs = observation_with_hands(3)
        state = adapter.parse(obs)
        assert obs["farms"][0]["hires_today"] == 3

    def test_parse_advanced_observation(self, adapter: ObservationAdapter) -> None:
        obs = observation_advanced(day=5, money=4500.0)
        state = adapter.parse(obs)
        assert state.current_day() == 5
        assert state.available_money() == 4500.0
        assert "NE" in state.farm.quadrants

    def test_parse_with_town_shops(self, adapter: ObservationAdapter) -> None:
        obs = observation_with_town(["FARMER_MARKET", "FISH_MONGER"])
        state = adapter.parse(obs)
        assert "FARMER_MARKET" in state.town.unlocked_shops

    def test_parse_with_market_prices(self, adapter: ObservationAdapter) -> None:
        obs = observation_with_market({"WHEAT": 25, "CARROT": 35})
        state = adapter.parse(obs)
        assert state.market.prices == {"WHEAT": 25, "CARROT": 35}

    def test_parse_with_animal_structure(self, adapter: ObservationAdapter) -> None:
        obs = observation_with_animal("GOOSE")
        state = adapter.parse(obs)
        assert state.farm.tiles is not None


class TestObservationAdapterEdgeCases:
    def test_parse_malformed_observation_raises(self, adapter: ObservationAdapter) -> None:
        with pytest.raises(Exception):
            adapter.parse(observation_malformed())

    def test_parse_partial_observation_raises(self, adapter: ObservationAdapter) -> None:
        with pytest.raises(Exception):
            adapter.parse(observation_partial())

    def test_parse_none_raises(self, adapter: ObservationAdapter) -> None:
        with pytest.raises(Exception):
            adapter.parse(None)  # type: ignore[arg-type]
