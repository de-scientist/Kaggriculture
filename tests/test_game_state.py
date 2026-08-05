from agent.domain import game_state as gs_domain
from agent.domain.season import Season


def test_game_state_defaults():
    state = gs_domain.GameState(player=0)
    assert state.player == 0
    assert state.current_day() == 0
    assert state.current_turn() == 0