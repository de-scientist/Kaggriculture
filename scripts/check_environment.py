#!/usr/bin/env python3
"""Environment validation script.

Verifies that the development/competition environment is correctly
configured by checking:

  * Python version
  * Required packages available
  * Project imports successfully
  * Configuration loads
  * Kaggle integration available (where installed)
  * Agent entry point callable

Usage:
    python scripts/check_environment.py
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
        lines = ["\n=== Environment Validation Report ===\n"]
        for name in self.passed:
            lines.append(f"  [PASS] {name}")
        for name in self.skipped:
            lines.append(f"  [SKIP] {name}")
        for name in self.failed:
            lines.append(f"  [FAIL] {name}")
        lines.append(
            f"\n{len(self.passed)} passed, {len(self.failed)} failed, "
            f"{len(self.skipped)} skipped"
        )
        return "\n".join(lines)


def check_python_version(result: _Result) -> None:
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 11:
        result.ok(f"Python {major}.{minor}")
    else:
        result.fail(
            "Python version",
            f"Python 3.11+ required, got {major}.{minor}",
        )


def check_required_packages(result: _Result) -> None:
    deps = [
        ("kaggle_environments", "kaggle-environments"),
        ("yaml", "pyyaml"),
    ]
    for import_name, pip_name in deps:
        try:
            __import__(import_name)
            result.ok(f"Package: {import_name}")
        except ImportError:
            result.fail(
                f"Package: {import_name}",
                f"Install with: pip install {pip_name}",
            )


def check_project_imports(result: _Result) -> None:
    try:
        from agent.agent import agent  # noqa: F401

        result.ok("Project imports (agent.agent)")
    except Exception as exc:
        result.fail("Project imports", f"{exc}\n{traceback.format_exc()}")

    try:
        from agent.domain.game_state import GameState  # noqa: F401

        result.ok("Project imports (domain)")
    except Exception as exc:
        result.fail("Domain imports", f"{exc}\n{traceback.format_exc()}")

    try:
        from agent.decision.decision_engine import decide  # noqa: F401

        result.ok("Project imports (decision)")
    except Exception as exc:
        result.fail("Decision imports", f"{exc}\n{traceback.format_exc()}")

    try:
        from agent.adapters import ActionAdapter, ObservationAdapter  # noqa: F401

        result.ok("Project imports (adapters)")
    except Exception as exc:
        result.fail("Adapter imports", f"{exc}\n{traceback.format_exc()}")


def check_configuration(result: _Result) -> None:
    try:
        from agent.config import get_config

        settings = get_config()
        result.ok(f"Configuration loaded (strategy={settings.strategy_name})")
    except Exception as exc:
        result.fail("Configuration", f"{exc}\n{traceback.format_exc()}")


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
        if isinstance(action, dict) and "farmer" in action:
            result.ok("Agent executes on observation")
        else:
            result.fail("Agent execution", f"Invalid action: {action}")
    except Exception as exc:
        result.fail("Agent execution", f"{exc}\n{traceback.format_exc()}")


def check_kaggle_integration(result: _Result) -> None:
    try:
        from kaggle_environments import make

        make("kaggriculture", debug=True)
        result.ok("Kaggle integration (kaggle-environments)")
    except ImportError:
        result.skip("Kaggle integration", "kaggle-environments not installed")
    except Exception as exc:
        result.fail("Kaggle integration", str(exc))


def main() -> int:
    result = _Result()

    check_python_version(result)
    check_required_packages(result)
    check_project_imports(result)
    check_configuration(result)
    check_agent_execution(result)
    check_kaggle_integration(result)

    print(result.report())
    return 0 if result.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
