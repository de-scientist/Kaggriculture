#!/usr/bin/env python3
"""Submission validation script for Kaggriculture competition (chapter 10).

Verifies that the agent package can be packaged and submitted to the
Kaggle competition by checking:

  * Required files exist (main.py, agent package)
  * Entry point exists and is callable
  * Imports resolve
  * Dependencies are available
  * Agent initialization works
  * Observation processing works
  * Decision generation works
  * Action serialization works
  * No fatal exceptions occur
  * Validation episode (if kaggle-environments available)

Usage:
    python scripts/validate_submission.py
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))


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
        ("yaml", "pyyaml", True),
        ("ruff", None, True),
        ("pytest", None, True),
        ("kaggle_environments", "kaggle-environments", False),
    ]
    for import_name, pip_name, required in deps:
        try:
            __import__(import_name)
            result.ok(f"Dependency available: {import_name}")
        except ImportError:
            if required:
                result.fail(
                    f"Dependency available: {import_name}",
                    f"pip install {pip_name or import_name}",
                )
            else:
                result.skip(
                    f"Dependency available: {import_name}",
                    f"Optional: pip install {pip_name or import_name}",
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
            result.fail(
                "Action has required keys",
                f"Missing: {required_keys - set(action.keys())}",
            )

        if isinstance(action.get("farmer"), list) and len(action["farmer"]) > 0:
            result.ok("Farmer action is non-empty list")
        else:
            result.fail("Farmer action is non-empty list", f"Got: {action.get('farmer')}")

    except Exception as exc:
        tb = traceback.format_exc()
        result.fail("Agent execution", f"{exc}\n{tb}")


def check_action_execution(result: _Result) -> None:
    """Verify the agent can execute on a valid observation."""
    check_agent_execution(result)


def check_decision_generation(result: _Result) -> None:
    """Verify the decision engine can generate a valid action."""
    try:
        from agent.adapters import ActionAdapter, ObservationAdapter
        from agent.config import get_config
        from agent.decision import decision_engine
        from agent.decision.decision_context import DecisionContext

        settings = get_config()
        adapter = ObservationAdapter()
        action_adapter = ActionAdapter()

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

        state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=state,
            config=settings,
            step=0,
            day=0,
            hour=0,
            remaining_turns=720,
            strategy_name="baseline",
        )

        action = decision_engine.decide(context)
        kaggle_action = action_adapter.convert(action)

        if isinstance(kaggle_action, dict) and "farmer" in kaggle_action:
            result.ok("Decision engine generates valid action")
        else:
            result.fail("Decision generation", f"Unexpected: {kaggle_action}")
    except Exception as exc:
        result.fail("Decision generation", f"{exc}\n{traceback.format_exc()}")


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


def check_entry_point(result: _Result) -> None:
    """Verify main.py exists and exposes the agent function."""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("main_entry", ROOT / "main.py")
        if spec is None or spec.loader is None:
            result.fail("Entry point", "Could not load main.py")
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "agent") and callable(mod.agent):
            result.ok("Entry point: main.py exposes agent function")
        else:
            result.fail("Entry point", "main.py does not expose 'agent' function")
    except Exception as exc:
        result.fail("Entry point", f"{exc}\n{traceback.format_exc()}")


def check_configuration(result: _Result) -> None:
    """Verify configuration loads correctly."""
    try:
        from agent.config import get_config

        settings = get_config()
        result.ok(f"Configuration loaded (strategy={settings.strategy_name})")
    except Exception as exc:
        result.fail("Configuration", f"{exc}\n{traceback.format_exc()}")


def check_observation_processing(result: _Result) -> None:
    """Verify the observation adapter processes a valid observation."""
    try:
        from agent.adapters import ObservationAdapter

        adapter = ObservationAdapter()
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
        state = adapter.parse(obs)
        if state is not None:
            result.ok("Observation processing works")
        else:
            result.fail("Observation processing", "Returned None")
    except Exception as exc:
        result.fail("Observation processing", f"{exc}\n{traceback.format_exc()}")


def check_action_serialization(result: _Result) -> None:
    """Verify the action adapter serializes a valid internal action."""
    try:
        from agent.adapters import ActionAdapter

        adapter = ActionAdapter()
        internal_action = {"farmer": ["PASS"], "hands": [], "market": []}
        kaggle_action = adapter.convert(internal_action)
        if "farmer" in kaggle_action and kaggle_action["farmer"] == ["PASS"]:
            result.ok("Action serialization works")
        else:
            result.fail("Action serialization", f"Unexpected: {kaggle_action}")
    except Exception as exc:
        result.fail("Action serialization", f"{exc}\n{traceback.format_exc()}")


def check_validation_episode(result: _Result) -> None:
    """Run a short episode against the Kaggle environment if available."""
    try:
        from kaggle_environments import make
    except ImportError:
        result.skip("Validation episode", "kaggle-environments not installed")
        return

    try:

        env = make("kaggriculture", debug=True)
        env.run(["main.py", "random"])
        final = env.steps[-1]
        statuses = [s.status for s in final]
        if all(s in ("DONE", "COMPLETE", "VALID") for s in statuses):
            result.ok("Validation episode completes without errors")
        else:
            result.fail("Validation episode", f"Statuses: {statuses}")
    except Exception as exc:
        result.fail("Validation episode", f"{exc}\n{traceback.format_exc()}")


def main() -> int:
    result = _Result()

    check_required_files(result)
    check_imports(result)
    check_entry_point(result)
    check_configuration(result)
    check_dependencies(result)
    check_observation_processing(result)
    check_action_execution(result)
    check_decision_generation(result)
    check_action_serialization(result)
    check_malformed_observation(result)
    check_validation_episode(result)

    print(result.report())
    return 0 if result.all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
