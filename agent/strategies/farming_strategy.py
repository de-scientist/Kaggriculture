"""Starter-style farming policy.

A self-contained wheat-production loop implemented directly on the raw
observation.  The agent tends the tile it stands on and walks between
unlocked tiles so the whole starting quadrant is productive:

* buy wheat seeds when the seed store is empty and affordable;
* plant wheat on an empty tile;
* water a young, unwatered plant (bonus window);
* harvest a plant that has reached its first yield day;
* dig weeds blocking the current tile;
* sell harvested wheat on the market;
* otherwise walk toward the nearest tile that needs work.

This deliberately mirrors the documented "Wheat Loop" so the behaviour is
predictable and easy to reason about, while extending it with movement so
more than a single tile is farmed.
"""

from __future__ import annotations

from typing import Any

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.strategies.strategy import ScoredAction, Strategy

WHEAT_SEED_COST = 10
WHEAT_FIRST_YIELD_DAY = 2


class FarmingStrategy(Strategy):
    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        try:
            action = self._decide(context.obs, context.player)
        except Exception:
            action = CandidateAction(
                id="pass", action_type="pass", estimated_reward=0.0
            )
        return [ScoredAction(action, 1.0, "farming_policy")]

    def _decide(self, obs: dict[str, Any], player: int) -> CandidateAction:
        farms = obs.get("farms")
        if not isinstance(farms, list) or player >= len(farms):
            return self._cand("pass")
        me = farms[player] or {}
        private = obs.get("private", {}) or {}
        seeds = private.get("seeds", {}) or {}
        shed = private.get("shed", {}) or {}

        tiles = me.get("tiles") or []
        if not isinstance(tiles, list) or not tiles:
            return self._cand("pass")
        height = len(tiles)
        width = len(tiles[0]) if isinstance(tiles[0], list) else height

        fx, fy = me.get("farmer") or (0, 0)
        if not (0 <= fy < height and 0 <= fx < width):
            return self._cand("pass")

        money = float(me.get("money", 0))
        unlocked = set(me.get("unlocked_quadrants", ["NW"]))
        day = int(obs.get("day", 0))

        wheat_seeds = int(seeds.get("WHEAT", 0))
        wheat_in_shed = int(shed.get("WHEAT", 0))

        tile = tiles[fy][fx]

        def in_bounds(x: int, y: int) -> bool:
            return 0 <= y < height and 0 <= x < width

        def quadrant(x: int, y: int) -> str:
            half = width // 2
            if x < half and y < half:
                return "NW"
            if x >= half and y < half:
                return "NE"
            if x < half and y >= half:
                return "SW"
            return "SE"

        def is_unlocked(x: int, y: int) -> bool:
            return in_bounds(x, y) and quadrant(x, y) in unlocked

        def kind(t: Any) -> str:
            if t is None:
                return "EMPTY"
            if t == "LOCKED":
                return "LOCKED"
            if isinstance(t, dict):
                return str(t.get("kind", "unknown")).upper()
            return "UNKNOWN"

        def plant_age(t: dict) -> int:
            return day - int(t.get("planted_day", day))

        cur = kind(tile)

        # 1. Clear a weed we are standing on.
        if cur == "WEED":
            return self._cand("dig")

        # 2. Harvest a mature plant on the current tile.
        if cur == "PLANT":
            if plant_age(tile) >= WHEAT_FIRST_YIELD_DAY and int(
                tile.get("yield_units", 0)
            ) > 0:
                return self._cand("harvest")
            # 3. Water a young plant that has not been watered yet.
            if not tile.get("watered_today", False):
                return self._cand("water")

        # 4. Plant wheat on an empty unlocked tile.
        if cur == "EMPTY" and is_unlocked(fx, fy) and wheat_seeds > 0:
            return self._cand("plant")

        # 5. Sell harvested wheat sitting in the shed.
        if wheat_in_shed > 0:
            return self._cand("sell", {"sell_count": wheat_in_shed})

        # 6. Buy seeds when we have fewer than the plantable tiles and can afford them.
        empty = sum(
            1
            for y in range(height)
            for x in range(width)
            if is_unlocked(x, y) and kind(tiles[y][x]) == "EMPTY"
        )
        if wheat_seeds < empty and money >= WHEAT_SEED_COST:
            buy = max(1, min(empty - wheat_seeds, int(money // WHEAT_SEED_COST)))
            return self._cand("buy_seed", {"buy_count": buy})

        # 7. Walk toward the nearest tile that needs work.
        target = self._nearest_work_tile(
            tiles, fx, fy, width, height, is_unlocked, kind, plant_age, wheat_seeds
        )
        if target is not None:
            step = self._step_toward(fx, fy, target[0], target[1], width, height, is_unlocked, tiles)
            if step is not None:
                return self._cand(step)

        return self._cand("pass")

    def _nearest_work_tile(
        self,
        tiles: list[list[Any]],
        fx: int,
        fy: int,
        width: int,
        height: int,
        is_unlocked,
        kind,
        plant_age,
        wheat_seeds: int,
    ):
        best = None
        best_score = None
        for y in range(height):
            for x in range(width):
                if x == fx and y == fy:
                    continue
                k = kind(tiles[y][x])
                dist = abs(x - fx) + abs(y - fy)
                score = None
                if k == "PLANT" and plant_age(tiles[y][x]) >= WHEAT_FIRST_YIELD_DAY and int(
                    tiles[y][x].get("yield_units", 0)
                ) > 0:
                    score = (0, dist)  # harvest is most urgent
                elif k == "PLANT" and not tiles[y][x].get("watered_today", False):
                    score = (1, dist)  # water
                elif k == "EMPTY" and wheat_seeds > 0:
                    score = (2, dist)  # plant
                if score is not None:
                    if best_score is None or score < best_score:
                        best_score = score
                        best = (x, y)
        return best

    def _step_toward(
        self,
        fx: int,
        fy: int,
        tx: int,
        ty: int,
        width: int,
        height: int,
        is_unlocked,
        tiles: list[list[Any]],
    ):
        dx = tx - fx
        dy = ty - fy
        options = []
        if dx != 0:
            nx = fx + (1 if dx > 0 else -1)
            if 0 <= nx < width and is_unlocked(nx, fy) and kind_safe(tiles, nx, fy) != "LOCKED":
                options.append(("east" if dx > 0 else "west", abs(dx)))
        if dy != 0:
            ny = fy + (1 if dy > 0 else -1)
            if 0 <= ny < height and is_unlocked(fx, ny) and kind_safe(tiles, fx, ny) != "LOCKED":
                options.append(("south" if dy > 0 else "north", abs(dy)))
        if not options:
            return None
        options.sort(key=lambda o: -o[1])
        return options[0][0]

    def _cand(self, action_type: str, metadata: dict[str, Any] | None = None) -> CandidateAction:
        return CandidateAction(
            id=action_type,
            action_type=action_type,
            estimated_reward=1.0,
            metadata=metadata or {},
        )


def kind_safe(tiles: list[list[Any]], x: int, y: int) -> str:
    t = tiles[y][x]
    if t is None:
        return "EMPTY"
    if t == "LOCKED":
        return "LOCKED"
    if isinstance(t, dict):
        return str(t.get("kind", "unknown")).upper()
    return "UNKNOWN"
