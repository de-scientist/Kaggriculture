from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.decision.fallback import get_fallback
from agent.decision.utility_score import compute_utility


def decide(context: DecisionContext) -> dict:
    from agent.decision.decision_engine import decide as _decide

    return _decide(context)


__all__ = [
    "CandidateAction",
    "DecisionContext",
    "compute_utility",
    "decide",
    "get_fallback",
]
