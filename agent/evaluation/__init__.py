"""Stage 3 — Self-play and tournament evaluation infrastructure.

This package provides a dependency-light framework for pitting agents against
each other (champion vs. challenger, Stage 3 vs. Stage 2, etc.) and reporting
win rates and average final coins.  The actual game runner is injected so the
framework is fully testable without the Kaggle runtime; a default runner using
``kaggle_environments`` is provided for real self-play.
"""

from __future__ import annotations

from agent.evaluation.tournament import (
    Agent,
    MatchResult,
    TournamentResult,
    run_match,
    run_tournament,
)

__all__ = [
    "Agent",
    "MatchResult",
    "TournamentResult",
    "run_match",
    "run_tournament",
]
