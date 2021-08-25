
'''Implements /src/Actions/index.ts'''
#from .game_objects import Player, Unit, City, CityTile
from .constants import Constants

UNIT_TYPES = Constants.UNIT_TYPES

class Action:
    def __init__(self, action, team):
        self.action = action
        self.team = team

class MoveAction(Action):
    def __init__(self, action, team, unitid, direction, newcell):
        self.unitid = unitid
        self.direction = direction
        self.newcell = newcell
        super().__init__(action, team)

class SpawnAction(Action):
    def __init__(self, action, team, unitid, x, y):
        self.unitid = unitid
        self.x = x
        self.y = y
        super().__init__(action, team)

class SpawnCartAction(SpawnAction):
    def __init__(self, action, team, unitid, x, y):
        self.type = UNIT_TYPES.CART
        super().__init__(action, team, unitid, x, y)

class SpawnWorkerAction(SpawnAction):
    def __init__(self, action, team, unitid, x, y):
        self.type = UNIT_TYPES.WORKER
        super().__init__(action, team, unitid, x, y)

class SpawnCityAction(Action):
    def __init__(self, action, team, unitid):
        self.unitid = unitid
        super().__init__(action, team)

class TransferAction(Action):
    def __init__(self, action, team, srcID, destID, resourceType, amount):
        self.srcID = srcID
        self.destID = destID
        self.resourceType = resourceType
        self.amount = amount
        super().__init__(action, team)

class PillageAction(Action):
    def __init__(self, action, team, unitid):
        self.unitid = unitid
        super().__init__(action, team)

class ResearchAction(Action):
    def __init__(self, action, team, x, y):
        self.x = x
        self.y = y
        super().__init__(action, team)

