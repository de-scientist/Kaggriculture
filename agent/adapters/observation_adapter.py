from agent.domain import game_state


def adapt(obs: dict) -> game_state.GameState:
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    market = obs["market"]
    town = obs["town"]

    return game_state.GameState(
        player=player,
        day=obs["day"],
        hour=obs["hour"],
        step=obs["step"],
        farms=obs["farms"],
        private=private,
        market=market,
        town=town,
    )