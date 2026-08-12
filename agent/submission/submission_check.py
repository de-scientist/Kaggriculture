"""Submission engineering: the Stage 4 competition compliance checklist (§72).

Provides programmatic checks that the submission package is valid and will not
crash on the Kaggle runtime:

* the package imports and exposes a callable ``agent``,
* a sample observation yields a structurally legal action dict,
* the agent never raises and never returns an illegal action across a full
  validation episode (when ``kaggle_environments`` is installed),
* the fail-safe wrapper is in place.

Run as a script (``python -m agent.submission.submission_check``) to print the
checklist and, with ``--write``, regenerate
``COMPETITION_COMPLIANCE_CHECKLIST.md``.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any

try:  # pragma: no cover - import path differs when run as a script
    from tests.fixtures.observations import minimal_observation
except Exception:  # pragma: no cover - fallback keeps the module importable
    def minimal_observation() -> dict[str, Any]:  # type: ignore[no-redef]
        return {
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


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    skipped: bool = False


@dataclass
class CheckSuite:
    results: list[CheckResult] = field(default_factory=list)

    def add(self, result: CheckResult) -> None:
        self.results.append(result)

    def all_passed(self) -> bool:
        return all(r.passed for r in self.results if not r.skipped)

    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed and not r.skipped)

    def total(self) -> int:
        return sum(1 for r in self.results if not r.skipped)


def _load_agent() -> Any:
    import main  # noqa: PLC0415 - submission surface is the package root

    return main.agent


def check_importable() -> CheckResult:
    try:
        _load_agent()
        return CheckResult("importable", True, "main.agent imports cleanly")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("importable", False, f"import failed: {exc}")


def check_agent_callable() -> CheckResult:
    try:
        agent = _load_agent()
    except Exception as exc:  # noqa: BLE001
        return CheckResult("agent_callable", False, f"could not import agent: {exc}")
    if callable(agent):
        return CheckResult("agent_callable", True, "main.agent is callable")
    return CheckResult("agent_callable", False, "main.agent is not callable")


def check_sample_action() -> CheckResult:
    try:
        agent = _load_agent()
        obs = minimal_observation()
        action = agent(obs)
    except Exception as exc:  # noqa: BLE001
        return CheckResult("sample_action", False, f"agent raised on sample obs: {exc}")
    if not isinstance(action, dict):
        return CheckResult("sample_action", False, "action is not a dict")
    if not isinstance(action.get("farmer"), list) or len(action.get("farmer", [])) == 0:
        return CheckResult("sample_action", False, "farmer action missing/empty")
    if not isinstance(action.get("hands"), list) or not isinstance(action.get("market"), list):
        return CheckResult("sample_action", False, "hands/market not lists")
    return CheckResult("sample_action", True, "sample observation yields a legal action dict")


def check_failsafe_present() -> CheckResult:
    try:
        from agent.submission.failsafe import FailSafeAgent

        agent = _load_agent()
        if isinstance(agent, FailSafeAgent):
            return CheckResult("failsafe", True, "submission wrapped in FailSafeAgent")
        return CheckResult("failsafe", False, "submission agent is not a FailSafeAgent instance")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("failsafe", False, f"could not verify failsafe: {exc}")


def check_validation_episode() -> CheckResult:
    try:
        from kaggle_environments import make
    except Exception:  # noqa: BLE001
        return CheckResult(
            "validation_episode",
            False,
            "kaggle_environments not installed; run `pip install kaggle-environments`",
            skipped=True,
        )
    try:
        agent = _load_agent()
        env = make("kaggriculture", configuration={"episodeSteps": 720})
        env.run([agent, "random"])
        final = env.steps[-1]
        rewards = [float(s.reward or 0.0) for s in final]
        if any(r <= 0 for r in rewards):
            return CheckResult("validation_episode", False, f"episode ended with reward {rewards}")
        return CheckResult("validation_episode", True, f"full episode vs random: rewards={rewards}")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("validation_episode", False, f"validation episode crashed: {exc}")


def run_all() -> CheckSuite:
    suite = CheckSuite()
    suite.add(check_importable())
    suite.add(check_agent_callable())
    suite.add(check_sample_action())
    suite.add(check_failsafe_present())
    suite.add(check_validation_episode())
    return suite


def render_markdown(suite: CheckSuite, suite_name: str = "Kaggriculture") -> str:
    lines = [f"# Competition Compliance Checklist — {suite_name}", ""]
    for r in suite.results:
        state = "SKIP" if r.skipped else ("PASS" if r.passed else "FAIL")
        lines.append(f"- [{state}] **{r.name}**: {r.detail}")
    lines.append("")
    if suite.total() == 0:
        lines.append("No runnable checks.")
    else:
        lines.append(f"Summary: {suite.passed()}/{suite.total()} passed.")
    return "\n".join(lines)


def main_cli() -> int:  # pragma: no cover - manual entry point
    suite = run_all()
    print(render_markdown(suite))
    if "--write" in sys.argv:
        with open("COMPETITION_COMPLIANCE_CHECKLIST.md", "w", encoding="utf-8") as fh:
            fh.write(render_markdown(suite))
        print("\nWrote COMPETITION_COMPLIANCE_CHECKLIST.md")
    return 0 if suite.all_passed() else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main_cli())
