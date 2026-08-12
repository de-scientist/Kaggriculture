"""Stage 4 submission-engineering package.

Contains the champion/challenger arena (:mod:`agent.submission.championship`),
the fail-safe wrapper (:mod:`agent.submission.failsafe`), and the submission
compliance checker (:mod:`agent.submission.submission_check`).
"""

from __future__ import annotations

from .failsafe import FailSafeAgent, EMERGENCY_ACTION, legalize, wrap_module

__all__ = ["FailSafeAgent", "EMERGENCY_ACTION", "legalize", "wrap_module"]
