from agent.adapters import observation_adapter


def test_adapt_returns_game_state():
    obs = {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "farms": [
            {
                "money": 3000,
                "tiles": [[None]],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            }
        ],
        "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {}, "prices": {}},
        "town": {"unlocked_shops": []},
    }
    state = observation_adapter.adapt(obs)
    assert state.player == 0
    assert state.current_day() == 0