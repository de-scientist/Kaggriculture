#!/usr/bin/env python3
"""Production-ready Kaggriculture agent for Stage 1."""

from typing import Dict, Any, List
import logging

from .adapters.observation_adapter import ObservationAdapter
from .adapters.action_serializer import ActionSerializer
from .decision.engine import DecisionEngine
from .config import Config
from .domain.entities import GameState

logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_config: Config = None
_adapter: ObservationAdapter = None
_serializer: ActionSerializer = None
_decision_engine: DecisionEngine = None


def build_agent(config: Dict[str, Any] = None) -> callable:
    global _config, _adapter, _serializer, _decision_engine
    if config is None:
        config = {}
    _config = Config(config)
    _adapter = ObservationAdapter(_config)
    _serializer = ActionSerializer(_config)
    _decision_engine = DecisionEngine(_config)

    def agent(obs: dict) -> Dict[str, Any]:
        try:
            domain_state: GameState = _adapter.adapt(obs)
            candidates = _decision_engine.generate_candidates(domain_state)
            valid_intents = _decision_engine.validate_actions(domain_state, candidates)
            scored_intents = _decision_engine.score_intents(domain_state, valid_intents)
            plan = _decision_engine.choose_actions(domain_state, scored_intents)
            action_dict = _serializer.serialize(plan)
            return action_dict
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return agent


def agent(obs: dict) -> Dict[str, Any]:
    if not _decision_engine:
        global _config, _adapter, _serializer, _decision_engine
        _config = Config({})
        _adapter = ObservationAdapter(_config)
        _serializer = ActionSerializer(_config)
        _decision_engine = DecisionEngine(_config)
    agent_func = build_agent({})
    return agent_func(obs)


if __name__ == "__main__":
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run([agent, "random"])
    final = env.steps[-1]
    for i, s in enumerate(final):
        print(f"Player {i}: reward={s.reward}, status={s.status}")
    env.render(mode="ipython", width=800, height=800)