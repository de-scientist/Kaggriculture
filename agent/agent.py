from agent.adapters import ActionAdapter, ObservationAdapter
from agent.config import settings
from agent.decision import decision_engine

_adapter = ObservationAdapter()
_action_adapter = ActionAdapter()


def agent(obs: dict) -> dict:
    player = obs["player"]

    context = decision_engine.DecisionContext(
        obs=obs,
        player=player,
        game_state=_adapter.parse(obs),
        config=settings.get_config(),
    )

    action = decision_engine.decide(context)
    kaggle_action = _action_adapter.convert(action)

    return kaggle_action
