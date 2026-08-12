"""Tests for the Stage 4 submission compliance checker (§72)."""

from __future__ import annotations

import main as main_module

from agent.submission import submission_check as sc
from agent.submission.failsafe import FailSafeAgent


def test_importable_and_callable() -> None:
    assert sc.check_importable().passed
    assert sc.check_agent_callable().passed


def test_sample_action_legal() -> None:
    res = sc.check_sample_action()
    assert res.passed, res.detail
    assert isinstance(main_module.agent, FailSafeAgent)


def test_failsafe_present_on_submission() -> None:
    res = sc.check_failsafe_present()
    assert res.passed, res.detail


def test_run_all_returns_suite() -> None:
    suite = sc.run_all()
    assert suite.total() >= 4
    # Import / callable / sample / failsafe must pass; validation episode may be
    # skipped when kaggle_environments is not installed.
    mandatory = [r for r in suite.results if r.name != "validation_episode"]
    assert all(r.passed for r in mandatory)


def test_render_markdown() -> None:
    text = sc.render_markdown(sc.run_all())
    assert "Compliance Checklist" in text
    assert "PASS" in text or "SKIP" in text
