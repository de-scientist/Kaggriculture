from __future__ import annotations

from agent.domain.farm import Farm
from agent.domain.inventory import Inventory
from agent.domain.market import Market
from agent.domain.player import Player
from agent.domain.season import Season
from agent.domain.town import Town
from agent.domain.weather import Weather


class GameState:
    __slots__ = (
        "_farm",
        "_inventory",
        "_market",
        "_opponent",
        "_player",
        "_season",
        "_step",
        "_town",
        "_weather",
    )

    def __init__(
        self,
        player: int = 0,
        farm: Farm | None = None,
        inventory: Inventory | None = None,
        market: Market | None = None,
        town: Town | None = None,
        season: Season | None = None,
        weather: Weather | None = None,
        opponent: Player | None = None,
        step: int = 0,
    ) -> None:
        self._player = player
        self._farm = farm or Farm()
        self._inventory = inventory or Inventory()
        self._market = market or Market()
        self._town = town or Town()
        self._season = season or Season()
        self._weather = weather or Weather()
        self._opponent = opponent or Player(index=1)
        self._step = step

    @property
    def player(self) -> int:
        return self._player

    @property
    def farm(self) -> Farm:
        return self._farm

    @property
    def inventory(self) -> Inventory:
        return self._inventory

    @property
    def market(self) -> Market:
        return self._market

    @property
    def town(self) -> Town:
        return self._town

    @property
    def season(self) -> Season:
        return self._season

    @property
    def weather(self) -> Weather:
        return self._weather

    @property
    def opponent(self) -> Player:
        return self._opponent

    @property
    def step(self) -> int:
        return self._step

    def current_day(self) -> int:
        return self._season.day

    def current_turn(self) -> int:
        return self._season.turn

    def remaining_turns(self) -> int:
        return self._season.remaining_turns

    def remaining_days(self) -> int:
        return self._season.remaining_days

    def available_money(self) -> float:
        return self._farm.money

    def available_workers(self) -> list:
        return self._farm.workers

    def current_market(self) -> Market:
        return self._market

    def advance_turn(self) -> GameState:
        new_season = self._season.advance_turn()
        return GameState(
            player=self._player,
            farm=self._farm,
            inventory=self._inventory,
            market=self._market,
            town=self._town,
            season=new_season,
            weather=self._weather,
            opponent=self._opponent,
            step=self._step + 1,
        )

    def __repr__(self) -> str:
        return (
            f"GameState(player={self._player}, "
            f"day={self._season.day}, "
            f"turn={self._season.turn}, "
            f"money={self._farm.money})"
        )
