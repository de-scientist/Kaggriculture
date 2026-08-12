#!/usr/bin/env python3
"""Kaggriculture AI — official submission surface.

This module is the entry point used by the Kaggle environment.  It delegates to
the Stage 2 runtime champion (:mod:`agent.runtime.agent`), which plans each
turn with the hybrid policy stack, records experience when enabled, and returns
a Kaggle-format action dict.  The legacy operational layer (:mod:`agent.agent`)
is kept for reference but is not used by the submission.

A single ``agent(obs)`` call per turn yields a Kaggle-format action dict.
"""

from __future__ import annotations

from typing import Any

from agent.runtime.agent import agent as _raw_agent
from agent.submission.failsafe import FailSafeAgent

__all__ = ["agent"]

# Outermost Stage 4 fail-safe layer: guarantees a legal action every turn so a
# single unexpected error can never zero the episode.
agent = FailSafeAgent(_raw_agent)


