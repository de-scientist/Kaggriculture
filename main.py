#!/usr/bin/env python3
"""Kaggriculture AI Platform - Main Submission

This is the official submission surface for the Kaggriculture Kaggle competition.
It provides the `agent` function that the Kaggle environment calls each turn.

This implementation is the deterministic Stage 1 baseline, matching the behavior
of the official `starter` agent while providing a foundation for future stages.

The agent uses a staged architecture with clean interfaces between components:
- ObservationAdapter: Converts raw obs to domain objects
- DomainModel: Pure business logic and game mechanics
- DecisionEngine: Orchestrates planners and strategies
- Strategies: Stage-specific implementations (deterministic -> heuristic -> economic -> utility)
- ActionValidator: Mirrors official engine preconditions
- ActionRanker: Multi-objective scoring and action selection
- ActionSerializer: Emits official action dict

Architecture ensures:
- Zero modification to official Kaggle engine
- Backward compatibility across stages
- Parity verification with official engine
- Performance budgets respected (<500ms per-step)
- Deterministic execution for testing

Author: Elite Software Engineering Organization
Version: 1.0.0 (Stage 0)
"""

from typing import Dict, Any, List
import logging

from kaggriculture_ai.adapters.observation_adapter import ObservationAdapter
from kaggriculture_ai.adapters.action_serializer import ActionSerializer
from kaggriculture_ai.decision.engine import DecisionEngine
from kaggriculture_ai.config import Config
from kaggriculture_ai.domain.entities import GameState

# Configure logging for production
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global configuration and components (initialized on first use)
_config: Config = None
_adapter: ObservationAdapter = None
_serializer: ActionSerializer = None
_decision_engine: DecisionEngine = None

def build_agent(config: Dict[str, Any] = None) -> callable:
    """Build and configure the agent function with dependencies.

    This function initializes the agent's components using the provided
    configuration. It follows the dependency injection pattern to ensure
    testability and maintainability.

    Args:
        config: Configuration dictionary with strategy settings.

    Returns:
        agent: Function that can be called by the Kaggle environment.
    """
    global _config, _adapter, _serializer, _decision_engine

    # Use defaults if no config provided
    if config is None:
        config = {}

    # Initialize configuration
    _config = Config(config)

    # Initialize components
    _adapter = ObservationAdapter(_config)
    _serializer = ActionSerializer(_config)
    _decision_engine = DecisionEngine(_config)

    def agent(obs: dict) -> Dict[str, Any]:
        """Agent function called by the Kaggle environment each turn.

        This is the main entry point called by the Kaggle framework. It receives
        the current observation and returns an action dict that will be applied
        in the next turn.

        Args:
            obs: Raw observation from the Kaggle environment containing
                current game state, market data, and player information.

        Returns:
            Action dict in the official Kaggle format:
            {
                "farmer": [op, ...args],
                "hands": [[op, ...args], ...],
                "market": [[op, ...args], ...]
            }

        Raises:
            KaggricultureAIError: If observation is invalid or processing fails.
        """
        try:
            # Step 1: Adapt observation to domain model
            # This is the only layer that touches raw dict protocol
            domain_state: GameState = _adapter.adapt(obs)

            # Step 2: Generate candidate actions using planners
            candidates = _decision_engine.generate_candidates(domain_state)

            # Step 3: Validate actions against engine preconditions
            valid_intents = _decision_engine.validate_actions(domain_state, candidates)

            # Step 4: Score and rank intents using current strategy
            scored_intents = _decision_engine.score_intents(domain_state, valid_intents)

            # Step 5: Choose best action per unit and build market orders
            plan = _decision_engine.choose_actions(domain_state, scored_intents)

            # Step 6: Serialize to official action format
            action_dict = _serializer.serialize(plan)

            # Step 7: Return to Kaggle framework
            return action_dict

        except Exception as e:
            # Log error and return PASS as fallback
            logger.error(f"Agent error: {e}", exc_info=True)
            return {"farmer": ["PASS"], "hands": [], "market": []}

    return agent


# For backward compatibility and direct usage
def agent(obs: dict) -> Dict[str, Any]:
    """Default agent function using default configuration.

    This function provides a simple default agent that can be used without
    needing to call build_agent first. It uses the deterministic Stage 1
    strategy by default.

    Args:
        obs: Raw observation from the Kaggle environment

    Returns:
        Action dict in the official Kaggle format
    """
    if not _decision_engine:
        # Initialize with default configuration
        global _config, _adapter, _serializer, _decision_engine
        _config = Config({})
        _adapter = ObservationAdapter(_config)
        _serializer = ActionSerializer(_config)
        _decision_engine = DecisionEngine(_config)

    # Reuse the build_agent logic by calling it with default config
    agent_func = build_agent({})
    return agent_func(obs)


if __name__ == "__main__":
    # For local testing and development
    from kaggle_environments import make

    def test_agent(obs: dict) -> Dict[str, Any]:
        """Test agent with sample observation."""
        return agent(obs)

    # Run a simple test if executed directly
    env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    env.run([test_agent, "random"])
    final = env.steps[-1]
    for i, s in enumerate(final):
        print(f"Player {i}: reward={s.reward}, status={s.status}")

    # Optional: render environment
    env.render(mode="ipython", width=800, height=800)
