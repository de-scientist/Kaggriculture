from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction


def get_fallback() -> CandidateAction:
    return CandidateAction(
        id="fallback_0",
        action_type="pass",
        estimated_cost=0.0,
        estimated_reward=0.0,
        metadata={"fallback": True},
    )
