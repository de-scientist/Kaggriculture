from agent.domain import game_state


def adapt(obs: dict) -> game_state.GameState:
    player = obs["player"]
    private = obs["private"]
    market = obs["market"]
    town = obs["town"]

    return game_state.GameState(
        player=player,
        step=obs["step"],
        farm=obs["farms"][player],
        private=private,
        market=market,
        town=town,
    )
