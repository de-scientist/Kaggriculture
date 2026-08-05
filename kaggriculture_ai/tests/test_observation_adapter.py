import pytest
from kaggriculture_ai.adapters.observation_adapter import ObservationAdapter
from kaggriculture_ai.exceptions import InvalidObservationError


def test_adapter_valid_observation():
    config = {}
    adapter = ObservationAdapter(config)
    obs = {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "farms": [{"money": 3000.0, "tiles": [], "farmer": [0, 0], "hands": [], "unlocked_quadrants": ["NW"], "hires_today": 0}],
        "market": {"inventory": {}, "prices": {}},
        "town": {"unlocked_shops": []},
        "private": {"shed": {}, "seeds": {}, "inventories": []},
    }
    result = adapter.adapt(obs)
    assert result is not None


def test_adapter_invalid_observation():
    config = {}
    adapter = ObservationAdapter(config)
    with pytest.raises(InvalidObservationError):
        adapter.adapt({})


def test_adapter_last_raw():
    config = {}
    adapter = ObservationAdapter(config)
    obs = {"test": "data"}
    adapter.adapt(obs)
    assert adapter.last_raw() == obs