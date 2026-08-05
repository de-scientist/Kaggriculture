from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction
from agent.decision.utility_score import compute_utility


def rank(
    actions: list[CandidateAction],
    game_state: Any,
) -> list[CandidateAction]:
    scored = [(compute_utility(a), a) for a in actions]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [a for _, a in scored]


def resolve_ties(
    actions: list[CandidateAction],
) -> list[CandidateAction]:
    return sorted(actions, key=lambda a: a.id)