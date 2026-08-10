import json
from typing import Any

from agent.domain import game_state
from agent.domain.market import Market
from agent.domain.season import Season
from agent.domain.town import Town


def serialize_game_state(state: game_state.GameState) -> dict[str, Any]:
    return {
        "player": state.player,
        "day": state.current_day(),
        "hour": state.current_turn(),
        "step": state.step,
        "farm": state.farm,
        "private": state.private,
        "market": state.market,
        "town": state.town,
    }


def deserialize_game_state(data: dict[str, Any]) -> game_state.GameState:
    return game_state.GameState(
        player=int(data["player"]),
        step=int(data["step"]),
        season=Season(day=int(data["day"]), turn=int(data["hour"])),
        market=data.get("market", Market()),
        town=data.get("town", Town()),
        private=data.get("private"),
    )


def serialize_action(action: dict[str, Any]) -> str:
    return json.dumps(action)


def deserialize_action(data: str) -> dict[str, Any]:
    return dict(json.loads(data))
