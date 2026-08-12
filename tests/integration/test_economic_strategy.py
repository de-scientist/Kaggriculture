"""Integration tests for Stage 2 economic strategy (Stage 2)."""

from __future__ import annotations

from typing import Any, ClassVar

from agent.decision.decision_context import DecisionContext
from agent.decision.decision_engine import decide
from agent.domain.game_state import GameState
from agent.strategies.economic_strategy import EconomicStrategy
from agent.strategies.strategy_manager import get_strategy


def _minimal_obs() -> dict[str, Any]:
    return {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "remaining_turns": 720,
        "farms": [
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
        ],
        "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {}, "prices": {}},
        "town": {"unlocked_shops": []},
    }


class TestEconomicStrategyRegistration:
    def test_economic_strategy_registered(self) -> None:
        from agent.strategies.strategy_manager import _STRATEGIES

        assert "economic" in _STRATEGIES

    def test_get_economic_strategy(self) -> None:
        strategy = get_strategy("economic")
        assert isinstance(strategy, EconomicStrategy)

    def test_unknown_strategy_falls_back(self) -> None:
        strategy = get_strategy("nonexistent")
        from agent.strategies.baseline_strategy import BaselineStrategy

        assert isinstance(strategy, BaselineStrategy)


class TestEconomicStrategyEvaluation:
    def test_evaluate_returns_scored_actions(self) -> None:
        strategy = EconomicStrategy()
        state = GameState(player=0, step=0)
        from agent.config import get_config

        settings = get_config()
        context = DecisionContext(
            obs=_minimal_obs(),
            player=0,
            game_state=state,
            config=settings,
            step=0,
            day=0,
            hour=0,
            remaining_turns=720,
            strategy_name="economic",
        )

        from agent.decision.candidate_actions import CandidateAction

        actions = [
            CandidateAction(id="1", action_type="pass"),
            CandidateAction(
                id="2", action_type="plant", estimated_reward=10.0, estimated_cost=10.0
            ),
        ]

        scored = strategy.evaluate(context, actions)
        assert len(scored) > 0
        assert all(hasattr(s, "score") for s in scored)

    def test_fallback_to_baseline_on_error(self) -> None:
        """Economic strategy must fall back to baseline on internal error."""
        strategy = EconomicStrategy()

        class BrokenGameState:
            @property
            def farm(self) -> Any:
                raise RuntimeError("Simulated error")

            private: ClassVar[dict[str, Any]] = {}
            market: ClassVar = None
            season: ClassVar = None

        context = DecisionContext(
            obs=_minimal_obs(),
            player=0,
            game_state=BrokenGameState(),
            config={},
        )

        from agent.decision.candidate_actions import CandidateAction

        actions = [CandidateAction(id="1", action_type="pass")]
        scored = strategy.evaluate(context, actions)
        assert len(scored) > 0


class TestEconomicStrategyWithDecisionEngine:
    def test_decision_engine_with_economic_strategy(self) -> None:
        """Verify the decision engine works with the economic strategy."""
        from agent.config import get_config, reset_config

        reset_config()
        settings = get_config()

        obs = _minimal_obs()
        state = GameState(player=0, step=0)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=state,
            config=settings,
            step=0,
            day=0,
            hour=0,
            remaining_turns=720,
            strategy_name="economic",
        )

        action = decide(context)
        assert isinstance(action, dict)
        assert "farmer" in action
        assert "hands" in action
        assert "market" in action
