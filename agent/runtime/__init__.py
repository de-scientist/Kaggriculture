"""Runtime agent: a faithful, dependency-free planner and agent entry point.

This package mirrors the kaggriculture engine directly (no shared-state
abstractions), implements the Stage 2 champion as a set of heuristic
policies, and hosts the hybrid champion/learned policy used for Stage 3.
"""

from .agent import agent
from .game import GameSnapshot
from .planner import TurnPlanner
from .settings import RuntimeSettings

__all__ = ["GameSnapshot", "RuntimeSettings", "TurnPlanner", "agent"]
