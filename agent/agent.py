from agent.adapters import observation_adapter, action_adapter
from agent.decision import decision_engine
from agent.config import settings


def agent(obs: dict) -> dict:
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    market = obs["market"]
    town = obs["town"]

    context = decision_engine.DecisionContext(
        obs=obs,
        player=player,
        game_state=observation_adapter.adapt(obs),
        config=settings.get_config(),
    )

    action = decision_engine.decide(context)
    kaggle_action = action_adapter.to_kaggle_format(action)

    return kaggle_action