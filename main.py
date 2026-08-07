#!/usr/bin/env python3
"""Kaggriculture AI — official submission surface.

This module is the entry point used by the Kaggle environment and by
``python -m agent.agent`` for local testing.  It delegates to the
fully-wired :mod:`agent.agent` module, which loads centralized configuration,
configures structured logging, and runs the decision engine with full
observability (tracing, metrics, telemetry, replay, performance budgets).

A single ``agent(obs)`` call per turn yields a Kaggle-format action dict.
"""
from __future__ import annotations

from typing import Any

from agent.agent import agent as _agent

__all__ = ["agent"]


def agent(obs: dict) -> dict[str, Any]:
    return _agent(obs)
