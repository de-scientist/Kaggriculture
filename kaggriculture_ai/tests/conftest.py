import pytest
from kaggriculture_ai.agent import agent, build_agent


@pytest.fixture
def sample_observation():
    return {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "farms": [
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
        ],
        "market": {
            "inventory": {"WHEAT": 10000, "CARROT": 10000},
            "prices": {"WHEAT": 25, "CARROT": 35},
        },
        "town": {"unlocked_shops": []},
        "private": {
            "shed": {},
            "seeds": {},
            "inventories": [[], []],
        },
    }


@pytest.fixture
def agent_fn():
    return build_agent({})