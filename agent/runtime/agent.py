"""Submission entry point for the runtime agent.

``agent(obs)`` is the Kaggle-facing function: it builds a ``GameSnapshot``,
plans the turn (champion or hybrid policy), records experience when enabled,
and returns the Kaggle action dict.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable, Mapping
from typing import Any

from .game import GameSnapshot
from .planner import TurnPlanner
from .policies import Policy, make_policy
from .settings import RuntimeSettings

logger = logging.getLogger(__name__)

_POLICY_ENV = os.environ.get("KAG_RUNTIME_POLICY", "auto")

AgentFn = Callable[[Mapping[str, Any]], dict[str, Any]]


class _AgentRuntime:
    """Cached planner + optional experience recorder for the process."""

    def __init__(self, policy: Policy | str | None = None) -> None:
        self.settings = RuntimeSettings.from_env()
        if isinstance(policy, Policy):
            self.policy = policy
        else:
            self.policy = make_policy(policy if policy is not None else _POLICY_ENV, self.settings)
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


def make_runtime_agent(
    policy: Policy | str | None = "auto",
    settings: RuntimeSettings | None = None,
) -> AgentFn:
    """Build a fresh, policy-parameterised submission agent callable.

    Used by the champion/challenger arena and the benchmark opponent suite to
    instantiate candidate agents that share the production planner but differ in
    their policy wrapper and/or planner settings.
    """
    rt = _AgentRuntime(policy)
    if settings is not None:
        rt.settings = settings
        rt.planner = TurnPlanner(settings=settings, policy=rt.policy)
    return lambda obs: rt.act(obs)


def get_runtime() -> _AgentRuntime:
    global _runtime
    if _runtime is None:
        _runtime = _AgentRuntime()
    return _runtime
