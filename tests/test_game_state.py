from agent.domain import game_state


def test_game_state_defaults():
    state = game_state.GameState(player=0)
    assert state.player == 0
    assert state.day == 0
    assert state.hour == 0