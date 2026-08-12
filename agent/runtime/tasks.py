"""Turn-level task generation and unit assignment.

Each owned tile yields at most one :class:`Task` (the single most valuable
operation available there).  Tasks are then greedily assigned to the closest
free unit, discounted by walking distance, and the planner converts a job into
either the tile/shed operation or the next move step.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .constants import (
    ANIMALS,
    CROPS,
    crop_base_price,
    is_ongoing,
    product_of,
)
from .crops import best_crop, crop_daily_value, cycle_days
from .game import GameSnapshot, Position
from .paths import distance, move_op_for_next_step, nearest_shed_tile, next_step
from .settings import RuntimeSettings

STEP_COST = 3.0

TILE_OPS = {
    "WATER",
    "HARVEST",
    "PLANT",
    "FEED",
    "CARE",
    "COLLECT_FERTILIZER",
    "FERTILIZE",
    "DIG",
    "BUILD_COOP",
    "BUILD_PASTURE",
    "PLACE",
    "PICKUP",
}


@dataclass(frozen=True)
class Task:
    """One actionable operation on one tile, with an estimated coin value."""

    pos: Position
    op: str
    arg: str | None
    value: float
    action_type: str
    reason: str


@dataclass
class Unit:
    """A worker (main farmer or hired hand) with its carried inventory."""

    id: int
    pos: Position
    inventory: Mapping[str, Any]


@dataclass(frozen=True)
class Job:
    """A task assigned to a unit, plus any shed item it must pick up first."""

    task: Task
    pickup_item: str | None = None
    pickup_count: int = 1


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def animal_value(animal: str, prices: Mapping[str, Any]) -> float:
    """Rough remaining value of an animal (replacement + product stream)."""
    spec = ANIMALS[animal]
    product = spec["product"]
    price = _num(prices.get(product), crop_base_price(product))
    product_stream = _num(spec["max_held"]) * price * 2
    return _num(spec["cost"]) * 0.4 + product_stream


def plot_value(snapshot: GameSnapshot, settings: RuntimeSettings) -> float:
    """Expected profit of freeing/using one tile with the best crop today."""
    crop = best_crop(snapshot, settings)
    if crop is None:
        return 0.0
    day_value = crop_daily_value(crop, snapshot.prices(), snapshot.day)
    return day_value * min(cycle_days(crop), max(1, snapshot.days_left()))


def _water_value(snapshot: GameSnapshot, tile: Mapping[str, Any]) -> float:
    crop = str(tile.get("crop", ""))
    if crop not in CROPS:
        return 0.0
    price = snapshot.price(crop)
    yield_units = _int(tile.get("yield_units"), 0)
    max_yield = _int(CROPS[crop]["max_yield"])
    if _int(tile.get("consecutive_unwatered"), 0) >= 1:
        # Becoming a weed tonight would lose the plant and all its potential.
        return max_yield * price * 0.9
    if is_ongoing(crop):
        return price * 0.25
    if snapshot.in_window(tile) and yield_units < max_yield:
        bonus = 2 if _int(tile.get("fertilized_until_day"), -1) >= snapshot.day else 1
        return min(bonus, max_yield - yield_units) * price
    return price * 0.5


def build_tasks(snapshot: GameSnapshot, settings: RuntimeSettings) -> list[Task]:
    """Build the best task for every owned unlocked tile."""
    tasks: list[Task] = []
    crop = best_crop(snapshot, settings)
    plant_budget = snapshot.seed_count(crop) if crop is not None else 0
    prices = snapshot.prices()

    cow_pending = _cows_pending(snapshot, settings)
    goose_pending = _geese_pending(snapshot, settings)

    for y in range(snapshot.board_size):
        for x in range(snapshot.board_size):
            tile = snapshot.tile_at(x, y)
            if tile == "LOCKED":
                continue
            pos = (x, y)
            if tile is None:
                if plant_budget > 0 and settings.plant_enabled:
                    tasks.append(
                        Task(pos, "PLANT", crop, plot_value(snapshot, settings), "plant", "empty")
                    )
                    plant_budget -= 1
                elif settings.enable_animals:
                    if cow_pending > 0 and _count_structures(snapshot, "PASTURE") < cow_pending:
                        tasks.append(
                            Task(
                                pos,
                                "BUILD_PASTURE",
                                None,
                                animal_value("COW", prices) * 0.6,
                                "build_pasture",
                                "animal",
                            )
                        )
                    elif goose_pending > 0 and _count_structures(snapshot, "COOP") < goose_pending:
                        tasks.append(
                            Task(
                                pos,
                                "BUILD_COOP",
                                None,
                                animal_value("GOOSE", prices) * 0.6,
                                "build_coop",
                                "animal",
                            )
                        )
                continue
            if not isinstance(tile, dict):
                continue
            kind = tile.get("kind")
            if kind == "WEED":
                tasks.append(
                    Task(pos, "DIG", None, plot_value(snapshot, settings) * 0.8, "dig", "weed")
                )
            elif kind == "PLANT":
                tasks.append(_plant_task(snapshot, settings, pos, tile))
            elif "animal" in tile:
                tasks.append(_animal_task(snapshot, pos, tile))
            elif kind in ("COOP", "PASTURE"):
                if settings.enable_animals:
                    if kind == "COOP" and goose_pending > 0:
                        tasks.append(
                            Task(
                                pos,
                                "PLACE",
                                "GOOSE",
                                animal_value("GOOSE", prices) * 0.8,
                                "place",
                                "goose_place",
                            )
                        )
                    elif kind == "PASTURE" and cow_pending > 0:
                        tasks.append(
                            Task(
                                pos,
                                "PLACE",
                                "COW",
                                animal_value("COW", prices) * 0.8,
                                "place",
                                "cow_place",
                            )
                        )
    tasks.sort(key=lambda t: -t.value)
    return tasks


def _count_structures(snapshot: GameSnapshot, structure: str) -> int:
    n = 0
    for y in range(snapshot.board_size):
        for x in range(snapshot.board_size):
            tile = snapshot.tile_at(x, y)
            if isinstance(tile, dict) and tile.get("kind") == structure:
                n += 1
    return n


def _count_animals(snapshot: GameSnapshot, animal: str) -> int:
    n = 0
    for y in range(snapshot.board_size):
        for x in range(snapshot.board_size):
            tile = snapshot.tile_at(x, y)
            if isinstance(tile, dict) and tile.get("animal") == animal:
                n += 1
    return n


def _cows_pending(snapshot: GameSnapshot, settings: RuntimeSettings) -> int:
    if not settings.enable_animals:
        return 0
    owned = _int(snapshot.shed().get("COW"), 0)
    placed = _count_animals(snapshot, "COW")
    return max(0, min(settings.cow_max - placed, owned))


def _geese_pending(snapshot: GameSnapshot, settings: RuntimeSettings) -> int:
    if not settings.enable_animals:
        return 0
    owned = _int(snapshot.shed().get("GOOSE"), 0)
    placed = _count_animals(snapshot, "GOOSE")
    return max(0, min(settings.goose_max - placed, owned))


def _plant_task(
    snapshot: GameSnapshot, settings: RuntimeSettings, pos: Position, tile: Mapping[str, Any]
) -> Task:
    crop = str(tile.get("crop", ""))
    age = snapshot.plant_age(tile, snapshot.day)
    price = snapshot.price(crop)
    yield_units = _int(tile.get("yield_units"), 0)
    if yield_units > 0 and age >= _int(CROPS[crop]["first_yield_day"]):
        return Task(pos, "HARVEST", None, yield_units * price, "harvest", "crop_ready")
    if not _int(tile.get("watered_today"), 0):
        value = _water_value(snapshot, tile)
        action_type = "water_bonus" if snapshot.in_window(tile) else "water"
        return Task(pos, "WATER", None, value, action_type, "plant")
    return Task(pos, "PASS", None, 0.0, "pass", "plant_done")


def _animal_task(snapshot: GameSnapshot, pos: Position, tile: Mapping[str, Any]) -> Task:
    animal = str(tile.get("animal", ""))
    prices = snapshot.prices()
    product = product_of(animal)
    yield_units = _int(tile.get("yield_units"), 0)
    if yield_units > 0:
        return Task(
            pos,
            "HARVEST",
            None,
            yield_units * _num(prices.get(product), 50.0),
            "harvest",
            "animal_product",
        )
    if not _int(tile.get("fed_today"), 0):
        return Task(pos, "FEED", None, animal_value(animal, prices) * 0.9, "feed", "animal_hungry")
    if not _int(tile.get("cared_today"), 0) and _int(tile.get("fed_today"), 0):
        return Task(pos, "CARE", None, _num(prices.get(product), 50.0), "care", "animal_care")
    if bool(tile.get("fertilizer_available")):
        return Task(pos, "COLLECT_FERTILIZER", None, 40.0, "collect", "fertilizer")
    return Task(pos, "PASS", None, 0.0, "pass", "animal_done")


def item_required(task: Task, unit: Unit, snapshot: GameSnapshot) -> str | None:
    if task.op == "FEED":
        if unit.inventory.get("WHEAT", 0) > 0:
            return None
        if _int(snapshot.shed().get("WHEAT"), 0) <= 0:
            return None
        return "WHEAT"
    if task.op == "PLACE":
        animal = str(task.arg or "")
        if unit.inventory.get(animal, 0) > 0:
            return None
        if _int(snapshot.shed().get(animal), 0) <= 0:
            return None
        return animal
    return None


def _job_distance(unit: Unit, task: Task, snapshot: GameSnapshot) -> float:
    board = snapshot.board_size
    need = item_required(task, unit, snapshot)
    if need is not None:
        shed = nearest_shed_tile(unit.pos, board)
        return float(distance(unit.pos, shed, board)) + float(distance(shed, task.pos, board))
    return float(distance(unit.pos, task.pos, board))


def assign_units(units: list[Unit], tasks: list[Task], snapshot: GameSnapshot) -> dict[int, Job]:
    """Greedily pair tasks to units by globally-best (value - distance) score."""
    jobs: dict[int, Job] = {}
    assigned_units: set[int] = set()
    remaining = list(tasks)
    while remaining:
        best_unit: Unit | None = None
        best_task: Task | None = None
        best_score = float("-inf")
        for task in remaining:
            for unit in units:
                if unit.id in assigned_units:
                    continue
                d = _job_distance(unit, task, snapshot)
                score = task.value - d * STEP_COST
                if score > best_score:
                    best_score = score
                    best_unit = unit
                    best_task = task
        if best_unit is None or best_task is None or best_score <= 0:
            break
        need = item_required(best_task, best_unit, snapshot)
        jobs[best_unit.id] = Job(task=best_task, pickup_item=need, pickup_count=1)
        assigned_units.add(best_unit.id)
        remaining.remove(best_task)
    return jobs


def job_to_op(job: Job | None, unit: Unit, snapshot: GameSnapshot) -> list[Any]:
    """Convert a unit's assigned job into this turn's action list."""
    if job is None:
        return ["PASS"]
    task = job.task
    board = snapshot.board_size
    need = item_required(task, unit, snapshot)
    if need is not None:
        shed = nearest_shed_tile(unit.pos, board)
        if shed == unit.pos:
            return ["PICKUP", need, job.pickup_count]
        nxt = next_step(unit.pos, shed, board)
        op = move_op_for_next_step(unit.pos, nxt) if nxt else None
        return [op] if op else ["PASS"]
    if unit.pos == task.pos:
        if task.op == "PASS":
            return ["PASS"]
        args = [task.arg] if task.arg else []
        return [task.op, *args]
    nxt = next_step(unit.pos, task.pos, board)
    op = move_op_for_next_step(unit.pos, nxt) if nxt else None
    return [op] if op else ["PASS"]


def target_hands(snapshot: GameSnapshot, settings: RuntimeSettings) -> int:
    target = settings.target_hands[0]
    for i, phase_day in enumerate(settings.hand_phase_days):
        if snapshot.day >= phase_day and i < len(settings.target_hands):
            target = settings.target_hands[i]
    return target
