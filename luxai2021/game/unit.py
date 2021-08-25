"""
Implements /src/Unit/index.ts -> Unit()
"""
from .actionable import Actionable
from .position import Position
from .resource import Resource
from .constants import Constants
from .game_constants import GAME_CONSTANTS
from .actions import *
import math

UNIT_TYPES = Constants.UNIT_TYPES

class Unit(Actionable):
    def __init__(self, x, y, type, team, configs, idcount):
        self.pos = Position(x, y)
        self.team = team
        self.type = type
        self.id = "u_" + idcount
        self.cargo = Cargo()
    
    def isWorker(self) -> bool:
        return self.type == UNIT_TYPES.WORKER

    def isCart(self) -> bool:
        return self.type == UNIT_TYPES.CART

    def getCargoSpaceLeft(self):
        """
        get cargo space left in this unit
        """
        spaceused = self.cargo.wood + self.cargo.coal + self.cargo.uranium
        if self.type == UNIT_TYPES.WORKER:
            return GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["WORKER"] - spaceused
        else:
            return GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["CART"] - spaceused

    def spendFuelToSurvive(self):
        """
        Implements /src/Unit/index.ts -> Unit.spendFuelToSurvive()
        """
        fuelNeeded = self.getLightUpkeep()
        woodNeeded = math.ceil(
            fuelNeeded / self.configs.parameters.RESOURCE_TO_FUEL_RATE.WOOD
        )
        woodUsed = min(self.cargo.wood, woodNeeded)
        fuelNeeded -= woodUsed * self.configs.parameters.RESOURCE_TO_FUEL_RATE.WOOD
        self.cargo.wood -= woodUsed
        if fuelNeeded <= 0:
            return True

        coalNeeded = math.ceil(
            fuelNeeded / self.configs.parameters.RESOURCE_TO_FUEL_RATE.COAL
        )
        coalUsed = min(self.cargo.coal, coalNeeded)
        fuelNeeded -= coalUsed * self.configs.parameters.RESOURCE_TO_FUEL_RATE.COAL
        self.cargo.coal -= coalUsed

        if fuelNeeded <= 0:
            return True

        uraniumNeeded = math.ceil(
            fuelNeeded / self.configs.parameters.RESOURCE_TO_FUEL_RATE.URANIUM
        )
        uraniumUsed = min(self.cargo.uranium, uraniumNeeded)
        fuelNeeded -= uraniumUsed * self.configs.parameters.RESOURCE_TO_FUEL_RATE.URANIUM
        self.cargo.uranium -= uraniumUsed

        if fuelNeeded <= 0:
            return True

        return fuelNeeded <= 0
    
    def canBuild(self, game_map) -> bool:
        """
        whether or not the unit can build where it is right now
        """
        cell = game_map.getCellByPos(self.pos)
        if not cell.hasResource() and self.canAct() and (self.cargo.wood + self.cargo.coal + self.cargo.uranium) >= GAME_CONSTANTS["PARAMETERS"]["CITY_BUILD_COST"]:
            return True
        return False

    def canAct(self) -> bool:
        """
        whether or not the unit can move or not. This does not check for potential collisions into other units or enemy cities
        """
        return self.cooldown < 1

    '''
    def move(self, dir) -> str:
        """
        return the command to move unit in the given direction
        """
        # TODO: Implement this action effect!
        return "m {} {}".format(self.id, dir)

    def transfer(self, dest_id, resourceType, amount) -> str:
        """
        return the command to transfer a resource from a source unit to a destination unit as specified by their ids
        """
        # TODO: Implement this action effect!
        return "t {} {} {} {}".format(self.id, dest_id, resourceType, amount)

    def build_city(self) -> str:
        """
        return the command to build a city right under the worker
        """
        # TODO: Implement this action effect!
        return "bcity {}".format(self.id)

    def pillage(self) -> str:
        """
        return the command to pillage whatever is underneath the worker
        """
        # TODO: Implement this action effect!
        return "p {}".format(self.id)
    '''




class Cargo:
    def __init__(self):
        self.wood = 0
        self.coal = 0
        self.uranium = 0

    def __str__(self) -> str:
        return f"Cargo | Wood: {self.wood}, Coal: {self.coal}, Uranium: {self.uranium}"




class Worker(Unit):
    """
    Worker class. Mirrors /src/Unit/index.ts -> Worker()
    """
    def __init__(self, x, y, team, configs, idcount):
        super().__init__(x, y, Unit.Type.WORKER, team, configs, idcount)
    
    def getLightUpkeep(self):
        return self.configs.parameters.LIGHT_UPKEEP.WORKER
    
    def canMove(self):
        return self.canAct()
    
    def expendResourcesForCity(self):
        # use wood, then coal, then uranium for building
        spentResources = 0
        for rtype in ["wood", "coal", "uranium"]:
            if (spentResources + self.cargo[rtype] > self.configs.parameters.CITY_BUILD_COST):
                rtypeSpent = self.configs.parameters.CITY_BUILD_COST - spentResources
                self.cargo[rtype] -= rtypeSpent
                break
            else:
                spentResources += self.cargo[rtype]
                self.cargo[rtype] = 0
    
    def turn(self, game):
        cell = game.map.getCellByPos(self.pos)
        isNight = game.isNight()
        cooldownMultiplier = 2 if isNight else 1

        if len(self.currentActions) == 1:
            action = self.currentActions[0]
            acted = True
            if isinstance(action, MoveAction):
                game.moveUnit(action.team, action.unitid, action.direction)
            elif isinstance(action, TransferAction):
                game.transferResources(
                    action.team,
                    action.srcID,
                    action.destID,
                    action.resourceType,
                    action.amount
                )
            elif isinstance(action, SpawnCityAction):
                game.spawnCityTile(action.team, self.pos.x, self.pos.y);
                self.expendResourcesForCity()
            elif isinstance(action, PillageAction):
                cell.road = max(
                    cell.road - self.configs.parameters.PILLAGE_RATE,
                    self.configs.parameters.MIN_ROAD
                )
            else:
                acted = False
            
            if acted:
                self.cooldown += self.configs.parameters.UNIT_ACTION_COOLDOWN.WORKER * cooldownMultiplier
    

class Cart(Unit):
    """
    Cart class. Mirrors /src/Unit/index.ts -> Cart()
    """
    def __init__(self, x, y, team, configs, idcount):
        super().__init__(x, y, Unit.Type.CART, team, configs, idcount)
    
    def getLightUpkeep(self):
        return self.configs.parameters.LIGHT_UPKEEP.CART
    
    def canMove(self):
        return self.canAct()
    
    def turn(self, game):
        cell = game.map.getCellByPos(self.pos)
        isNight = game.isNight()
        cooldownMultiplier = 2 if isNight else 1
        
        if len(self.currentActions) == 1:
            action = self.currentActions[0]
            acted = True
            if isinstance(action, MoveAction):
                game.moveUnit(action.team, action.unitid, action.direction)
                self.cooldown += self.configs.parameters.UNIT_ACTION_COOLDOWN.CART * cooldownMultiplier
            elif isinstance(action, TransferAction):
                game.transferResources(
                    action.team,
                    action.srcID,
                    action.destID,
                    action.resourceType,
                    action.amount
                )
            self.cooldown += self.configs.parameters.UNIT_ACTION_COOLDOWN.CART * cooldownMultiplier
        
        endcell = game.map.getCellByPos(self.pos)

        # auto create roads by increasing the cooldown value of the the cell unit is on currently
        if endcell.getRoad() < self.configs.parameters.MAX_ROAD:
            endcell.road = min(
                endcell.road + self.configs.parameters.CART_ROAD_DEVELOPMENT_RATE,
                self.configs.parameters.MAX_ROAD
            )
            game.stats.teamStats[self.team].roadsBuilt += self.configs.parameters.CART_ROAD_DEVELOPMENT_RATE;
        
