from typing import Dict, Any, Optional
from ..domain.entities import GameState, Turn, Season
from ..interfaces.observation_adapter import IObservationAdapter
from ..exceptions import InvalidObservationError


class ObservationAdapter(IObservationAdapter):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._last_raw: Optional[Dict[str, Any]] = None

    def adapt(self, raw_observation: Dict[str, Any]) -> GameState:
        try:
            self._last_raw = raw_observation
            self._validate_schema(raw_observation)
            turn = Turn(
                day=raw_observation["day"],
                hour=raw_observation["hour"],
                step=raw_observation.get("step", 0),
            )
            season = Season(
                turn_count=turn.step,
                turns_per_day=24,
                days=30,
            )
            game_state = GameState(
                turn=turn,
                season=season,
                raw=raw_observation,
            )
            return game_state
        except Exception as e:
            raise InvalidObservationError(f"Invalid observation: {e}") from e

    def _validate_schema(self, observation: Dict[str, Any]) -> None:
        required_keys = ["player", "day", "hour", "farms", "market", "town", "private"]
        for key in required_keys:
            if key not in observation:
                raise InvalidObservationError(f"Missing required key: {key}")

    def last_raw(self) -> Dict[str, Any]:
        if self._last_raw is None:
            raise RuntimeError("No observation has been adapted yet")
        return self._last_raw