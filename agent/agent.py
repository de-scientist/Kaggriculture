from agent.adapters import action_adapter, observation_adapter
from agent.config import settings
from agent.decision import decision_engine


def agent(obs: dict) -> dict:
    player = obs["player"]

    context = decision_engine.DecisionContext(
        obs=obs,
        player=player,
        game_state=observation_adapter.adapt(obs),
        config=settings.get_config(),
    )

    action = decision_engine.decide(context)
    kaggle_action = action_adapter.to_kaggle_format(action)

    return kaggle_action
