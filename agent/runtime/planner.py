"""Turn planner: assembles the final Kaggle action dict for one observation.

Flow: observation -> :class:`GameSnapshot` -> policy adjustments ->
tasks -> unit assignment -> farmer/hand ops -> market orders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .game import GameSnapshot
from .settings import RuntimeSettings
from .tasks import Job, Task, Unit, assign_units, build_tasks, job_to_op
from .market import plan_market_orders
from .policies import Policy


@dataclass
class TurnPlan:
    """Everything produced for one turn, including diagnostics for learning."""

    farmer_op: list[Any]
    hands_ops: list[list[Any]]
    market_orders: list[list[Any]]
    candidates: list[Task] = field(default_factory=list)
    farmer_action_type: str = "pass"
    info: dict[str, Any] = field(default_factory=dict)

    @property
    def action(self) -> dict[str, Any]:
        return {"farmer": self.farmer_op, "hands": self.hands_ops, "market": self.market_orders}


def _units(snapshot: GameSnapshot) -> list[Unit]:
    inventories = snapshot.inventories()
    out: list[Unit] = [Unit(0, snapshot.farmer_pos(), inventories[0] if inventories else {})]
    for i, pos in enumerate(snapshot.hands()):
        inv = inventories[i + 1] if i + 1 < len(inventories) else {}
        out.append(Unit(i + 1, pos, inv))
    return out


class TurnPlanner:
    """Runs the champion plan, optionally wrapped by a learning policy."""

    def __init__(self, settings: RuntimeSettings | None = None, policy: Policy | None = None) -> None:
        self.settings = settings if settings is not None else RuntimeSettings.from_env()
        self.policy = policy

    def plan(self, snapshot: GameSnapshot) -> TurnPlan:
        eff_settings, adjustments = self._apply_policy(snapshot)
        tasks = build_tasks(snapshot, eff_settings)
        tasks = self._rank_tasks(snapshot, tasks, eff_settings)
        orders = plan_market_orders(snapshot, eff_settings)
        units = _units(snapshot)
        jobs = assign_units(units, tasks, snapshot)

        farmer_unit = units[0]
        farmer_job = jobs.get(0)
        farmer_op = job_to_op(farmer_job, farmer_unit, snapshot)
        hands_ops = [job_to_op(jobs.get(u.id), u, snapshot) for u in units[1:]]

        farmer_type = _action_type(farmer_op, farmer_job)
        plan = TurnPlan(
            farmer_op=farmer_op,
            hands_ops=hands_ops,
            market_orders=orders,
            candidates=tasks,
            farmer_action_type=farmer_type,
            info={
                "policy": "champion" if self.policy is None else type(self.policy).__name__,
                "adjustments": adjustments,
                "settings": eff_settings,
                "n_tasks": len(tasks),
                "n_jobs": len(jobs),
            },
        )
        return plan

    def _apply_policy(self, snapshot: GameSnapshot) -> tuple[RuntimeSettings, dict[str, Any]]:
        if self.policy is None:
            return self.settings, {}
        return self.policy.adjust(snapshot, self.settings)


def _action_type(farmer_op: list[Any], job: Job | None) -> str:
    if job is not None:
        return job.task.action_type
    op = farmer_op[0] if farmer_op else "PASS"
    if op in ("NORTH", "SOUTH", "EAST", "WEST"):
        return "move"
    return "pass"
