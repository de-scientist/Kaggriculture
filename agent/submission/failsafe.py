"""Submission fail-safe hierarchy for Stage 4.

The Kaggle environment expects ``agent(obs)`` to return a legal action dict
every single turn.  A single unhandled exception zeroes the episode.  This
module provides the last-resort layer required by the Stage 4 robustness plan
(§91-92): a wrapper that catches any failure and returns a guaranteed-legal
emergency action, plus a structural ``legalize`` step that repairs malformed
dicts before they leave the process.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from typing import Any

logger = logging.getLogger(__name__)

AgentFn = Callable[[Mapping[str, Any]], dict[str, Any]]

EMERGENCY_ACTION: dict[str, Any] = {"farmer": ["PASS"], "hands": [], "market": []}


def legalize(action: Any) -> dict[str, Any]:
    """Coerce an arbitrary value into a structurally legal Kaggle action dict.

    Returns :data:`EMERGENCY_ACTION` when the value is not a usable dict.
    """
    if not isinstance(action, dict):
        return dict(EMERGENCY_ACTION)
    farmer = action.get("farmer")
    if not isinstance(farmer, list) or len(farmer) == 0:
        farmer = ["PASS"]
    hands = action.get("hands")
    if not isinstance(hands, list):
        hands = []
    market = action.get("market")
    if not isinstance(market, list):
        market = []
    return {"farmer": farmer, "hands": hands, "market": market}


class FailSafeAgent:
    """Wrap an agent callable so it can never crash the episode.

    On any exception (or malformed return) it logs the failure and returns the
    emergency :data:`EMERGENCY_ACTION`.  This is the outermost layer of the
    Stage 4 fail-safe hierarchy:

    ``Championship Hybrid -> Stage 3 Hybrid -> Stage 2 Planner -> Stage 1
    Baseline -> Emergency Fallback``.
    """

    def __init__(self, agent_fn: AgentFn, *, logger: logging.Logger | None = None) -> None:
        self._agent = agent_fn
        self._log = logger or logging.getLogger(__name__)

    def __call__(self, obs: Mapping[str, Any], configuration: Any = None) -> dict[str, Any]:
        """Callable entry point.

        Tolerates the Kaggle calling convention ``agent(observation,
        configuration)`` (the second argument is ignored here) so a signature
        mismatch can never surface as an unhandled error to the environment.
        """
        try:
            out = self._agent(obs)
        except Exception:  # noqa: BLE001 - the whole point is to catch everything
            self._log.exception("agent raised; returning emergency fallback action")
            return dict(EMERGENCY_ACTION)
        return legalize(out)


def wrap_module(agent_fn: AgentFn) -> AgentFn:
    """Convenience: return a fail-safe-wrapped copy of ``agent_fn``."""
    return FailSafeAgent(agent_fn)
