from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext


def generate_candidates(context: DecisionContext) -> list[CandidateAction]:
    candidates: list[CandidateAction] = []
    candidates.append(
        CandidateAction(
            id="harvest_0",
            action_type="harvest",
            estimated_cost=0.0,
            estimated_reward=10.0,
            metadata={"priority": 1},
        )
    )
    candidates.append(
        CandidateAction(
            id="water_0",
            action_type="water",
            estimated_cost=0.0,
            estimated_reward=5.0,
            metadata={"priority": 2},
        )
    )
    candidates.append(
        CandidateAction(
            id="plant_0",
            action_type="plant",
            estimated_cost=10.0,
            estimated_reward=15.0,
            metadata={"priority": 3},
        )
    )
    candidates.append(
        CandidateAction(
            id="sell_0",
            action_type="sell",
            estimated_cost=0.0,
            estimated_reward=8.0,
            metadata={"priority": 4},
        )
    )
    candidates.append(
        CandidateAction(
            id="pass_0",
            action_type="pass",
            estimated_cost=0.0,
            estimated_reward=0.0,
            metadata={"priority": 99},
        )
    )
    return candidates