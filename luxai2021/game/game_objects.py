from typing import Dict

from .constants import Constants
from .position import Position
from .game_constants import GAME_CONSTANTS
from .actions import *
from .actionable import Actionable

import math

UNIT_TYPES = Constants.UNIT_TYPES


class City:
    def __init__(self, teamid, cityid, fuel, light_upkeep):
        self.cityid = cityid
        self.team = teamid
        self.fuel = fuel
        self.citytiles: list[CityTile] = []
        self.light_upkeep = light_upkeep
    
    def _addCityTile(self, x, y, cooldown):
        ct = CityTile(self.team, self.cityid, x, y, cooldown)
        self.citytiles.append(ct)
        return ct
    
    def getLightUpkeep(self):
        return self.light_upkeep


class CityTile:
    def __init__(self, teamid, cityid, x, y, cooldown):
        self.cityid = cityid
        self.team = teamid
        self.pos = Position(x, y)
        self.cooldown = cooldown
    
    def canAct(self) -> bool:
        """
        Whether or not this unit can research or build
        """
        return self.cooldown < 1
    
    def research(self) -> str:
        """
        returns command to ask this tile to research this turn
        """
        # TODO: Implement this action effect!
        return "r {} {}".format(self.pos.x, self.pos.y)
    
    def buildWorker(self) -> str:
        """
        returns command to ask this tile to build a worker this turn
        """
        # TODO: Implement this action effect!
        return "bw {} {}".format(self.pos.x, self.pos.y)
    
    def buildCart(self) -> str:
        """
        returns command to ask this tile to build a cart this turn
        """
        # TODO: Implement this action effect!
        return "bc {} {}".format(self.pos.x, self.pos.y)
