'''Implements /src/Game/city.ts'''

from .actionable import Actionable
from .position import Position
from .resource import Resource
from .actions import *
import math

'''
//**
 * A city is composed of adjacent city tiles of the same team
 */
 '''
class City:
    def __init__(self, team, configs, idcount, cityid = None, fuel = 0):
        self.team = team
        self.configs = configs
        if cityid:
            self.id = cityid
        else:
            self.id = "c_%i" % idcount
        self.fuel = fuel
        self.citycells = []
    
    def getLightUpkeep(self):
        return len(self.citycells) * self.configs["parameters"]["LIGHT_UPKEEP"]["CITY"] - self.getAdjacencyBonuses()
    
    def getAdjacencyBonuses(self):
        bonus = 0
        for cell in self.citycells:
            bonus += cell.citytile.adjacentCityTiles * self.configs["parameters"]["CITY_ADJACENCY_BONUS"]
        return bonus
    
    def addCityTile(self, cell):
        self.citycells.append(cell)


class CityTile(Actionable):
    def __init__(self, team, configs, cooldown=0.0) -> None:
        self.team = team
        self.pos = None
        self.cityid = None
        self.adjacentCityTiles = 0
        super().__init__(configs, cooldown)
    
    def getTileID(self):
        return f"{{self.cityid}}_{{self.pos.x}}_{{self.pos.y}}"
    
    def canBuildUnit(self):
        return self.canAct()
    
    def canResearch(self):
        return self.canAct()
    
    def getCargoSpaceLeft(self):
        return 9999999 # Infinite space

    def turn(self, game):
        if (len(self.currentActions) == 1):
            action = self.currentActions[0]
            if isinstance(action, SpawnCartAction):
                game.spawnCart(action.team, action.x, action.y)
                self.resetCooldown()
            elif isinstance(action, SpawnWorkerAction):
                game.spawnWorker(action.team, action.x, action.y);
                self.resetCooldown()
            elif isinstance(action, ResearchAction):
                self.resetCooldown()
                game.state.teamStates[self.team]["researchPoints"] += 1
                if ( game.state["teamStates"][self.team]["researchPoints"] >= self.configs["parameters"]["RESEARCH_REQUIREMENTS"]["COAL"] ):
                    game.state.teamStates[self.team]["researched"]["coal"] = True
                if ( game.state.teamStates[self.team]["researchPoints"] >= self.configs["parameters"]["RESEARCH_REQUIREMENTS"]["URANIUM"] ):
                    game.state.teamStates[self.team]["researched"]["uranium"] = True
            
        if (self.cooldown > 0):
            self.cooldown -= 1

    def resetCooldown(self):
        self.cooldown = self.configs["parameters"]["CITY_ACTION_COOLDOWN"]

    
    
    
