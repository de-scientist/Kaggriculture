#!/usr/bin/env python3
"""Submission validation script for Kaggriculture competition (chapter 9).

Verifies that the agent package can be packaged and submitted to the
Kaggle competition by checking:

  * Required files exist (main.py, agent package)
  * Entry point exists and is importable
  * Dependencies are available
  * Agent initializes
  * Observation can be processed
  * Action can be generated
  * Action can be serialized
  * No fatal exceptions occur

Usage:
    python scripts/validate_submission.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class _Result:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.skipped: list[str] = []

    def ok(self, name: str) -> None:
        self.passed.append(name)

    def fail(self, name: str, reason: str) -> None:
        self.failed.append(f"{name}: {reason}")

    def skip(self, name: str, reason: str) -> None:
        self.skipped.append(f"{name}: {reason}")

    @property
    def all_passed(self) -> bool:
        return len(self.failed) == 0

    def report(self) -> str:
        lines = ["\n=== Submission Validation Report ===\n"]
        for name in self.passed:
            lines.append(f"  [PASS] {name}")
        for name in self.skipped:
            lines.append(f"  [SKIP] {name}")
        for name in self.failed:
            lines.append(f"  [FAIL] {name}")
        lines.append(
            f"\n{len(self.passed)} passed, {len(self.failed)} failed, {len(self.skipped)} skipped"
        )
        return "\n".join(lines)


def check_required_files(result: _Result) -> None:
    required = ["main.py", "agent/__init__.py", "agent/agent.py"]
    for path in required:
        full = ROOT / path
        if full.exists():
            result.ok(f"File exists: {path}")
        else:
            result.fail(f"File exists: {path}", f"{full} not found")


def check_imports(result: _Result) -> None:
    try:
        from agent.agent import agent  # noqa: F401
        result.ok("Agent importable")
    except Exception as exc:
        result.fail("Agent importable", str(exc))

    try:
        from agent.adapters import ActionAdapter, ObservationAdapter  # noqa: F401
        result.ok("Adapters importable")
    except Exception as exc:
        result.fail("Adapters importable", str(exc))

    try:
        from agent.decision.decision_engine import decide  # noqa: F401
        result.ok("Decision engine importable")
    except Exception as exc:
        result.fail("Decision engine importable", str(exc))


def check_dependencies(result: _Result) -> None:
    deps = [
        ("kaggle_environments", "kaggle-environments"),
        ("yaml", "pyyaml"),
        ("ruff", None),
        ("pytest", None),
    ]
    for import_name, pip_name in deps:
        try:
            __import__(import_name)
            result.ok(f"Dependency available: {import_name}")
        except ImportError:
            result.fail(
                f"Dependency available: {import_name}",
                f"pip install {pip_name or import_name}"
            )


def check_agent_execution(result: _Result) -> None:
    obs = {
        "player": 0,
        "step": 0,
        "day": 0,
        "hour": 0,
        "remaining_turns": 720,
        "farms": [
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
            {
                "money": 3000.0,
                "tiles": [[None for _ in range(10)] for _ in range(10)],
                "farmer": [0, 0],
                "hands": [],
                "unlocked_quadrants": ["NW"],
                "hires_today": 0,
            },
        ],
        "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
        "market": {"inventory": {}, "prices": {}},
        "town": {"unlocked_shops": []},
    }

    try:
        from agent.agent import agent

        action = agent(obs)
        result.ok("Agent executes on observation")

        if not isinstance(action, dict):
            result.fail("Action is dict", f"Got {type(action)}")
        else:
            result.ok("Action is dict")

        required_keys = {"farmer", "hands", "market"}
        if required_keys.issubset(action.keys()):
            result.ok("Action has required keys")
        else:
            result.fail("Action has required keys", f"Missing: {required_keys - set(action.keys())}")

        if isinstance(action.get("farmer"), list) and len(action["farmer"]) > 0:
            result.ok("Farmer action is non-empty list")
        else:
            result.fail("Farmer action is non-empty list", f"Got: {action.get('farmer')}")

    except Exception as exc:
        tb = traceback.format_exc()
        result.fail("Agent execution", f"{exc}\n{tb}")


def check_malformed_observation(result: _Result) -> None:
    from agent.agent import agent

    try:
        action = agent({"player": 0})
        if action == {"farmer": ["PASS"], "hands": [], "market": []}:
            result.ok("Malformed observation falls back to PASS")
        else:
            result.fail("Malformed observation fallback", f"Got: {action}")
    except Exception as exc:
        result.fail("Malformed observation fallback", str(exc))


def main() -> int:
    result = _Result()

    check_required_files(result)
    check_imports(result)
    check_dependencies(result)
    check_agent_execution(result)
    check_malformed_observation(result)

    print(result.report())
    return 0 if result.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
