from __future__ import annotations

from agent.decision.candidate_actions import CandidateAction


def filter_by_resources(
    actions: list[CandidateAction],
    available_money: float,
) -> list[CandidateAction]:
    return [a for a in actions if a.estimated_cost <= available_money]


def filter_by_worker_availability(
    actions: list[CandidateAction],
    available_workers: int,
) -> list[CandidateAction]:
    if available_workers <= 0:
        return [a for a in actions if a.action_type.lower() == "pass"]
    return actions


def filter_by_ownership(
    actions: list[CandidateAction],
    owned_tiles: set[tuple[int, int]],
) -> list[CandidateAction]:
    return [
        a
        for a in actions
        if a.target_position is None or a.target_position in owned_tiles
    ]


def filter_pre_validation(
    actions: list[CandidateAction],
    available_money: float,
    available_workers: int,
    owned_tiles: set[tuple[int, int]],
) -> list[CandidateAction]:
    result = filter_by_resources(actions, available_money)
    result = filter_by_worker_availability(result, available_workers)
    result = filter_by_ownership(result, owned_tiles)
    return result