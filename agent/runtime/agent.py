"""Submission entry point for the runtime agent.

``agent(obs)`` is the Kaggle-facing function: it builds a ``GameSnapshot``,
plans the turn (champion or hybrid policy), records experience when enabled,
and returns the Kaggle action dict.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Mapping

from .game import GameSnapshot
from .planner import TurnPlanner
from .policies import make_policy
from .settings import RuntimeSettings

logger = logging.getLogger(__name__)

_POLICY_ENV = os.environ.get("KAG_RUNTIME_POLICY", "auto")


class _AgentRuntime:
    """Cached planner + optional experience recorder for the process."""

    def __init__(self) -> None:
        self.settings = RuntimeSettings.from_env()
        self.policy = make_policy(_POLICY_ENV, self.settings)
        self.planner = TurnPlanner(settings=self.settings, policy=self.policy)
        self.recorder = None
        if self.settings.record_experience:
            try:
                from ..learning.experience import ExperienceRecorder

                self.recorder = ExperienceRecorder(directory=self.settings.experience_dir)
            except Exception:  # pragma: no cover - recorder must never break play
                logger.exception("failed to initialize experience recorder")

    def act(self, obs: Mapping[str, Any]) -> dict[str, Any]:
        snapshot = GameSnapshot.from_obs(obs)
        started = time.perf_counter()
        plan = self.planner.plan(snapshot)
        elapsed = (time.perf_counter() - started) * 1000.0
        if self.recorder is not None:
            try:
                self.recorder.observe(snapshot, plan)
            except Exception:  # pragma: no cover - recording is best-effort
                logger.exception("failed to record experience turn")
        plan.info["latency_ms"] = elapsed
        return plan.action


_runtime: _AgentRuntime | None = None


def agent(obs: Mapping[str, Any]) -> dict[str, Any]:
    global _runtime
    if _runtime is None:
        _runtime = _AgentRuntime()
    return _runtime.act(obs)


def get_runtime() -> _AgentRuntime:
    global _runtime
    if _runtime is None:
        _runtime = _AgentRuntime()
    return _runtime
