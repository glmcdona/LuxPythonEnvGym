
'''Implements /src/Actions/index.ts'''
#from .game_objects import Player, Unit, City, CityTile
from .constants import Constants

UNIT_TYPES = Constants.UNIT_TYPES

class Action:
    def __init__(self, action, team):
        self.action = action
        self.team = team

class MoveAction(Action):
    def __init__(self, team, unitid, direction, **kwarg):
        if unitid == None:
            raise Exception("Move action needs a unit.")

        action = Constants.ACTIONS.MOVE
        self.unitid = unitid
        self.direction = direction
        super().__init__(action, team)

class SpawnAction(Action):
    def __init__(self, action, team, unitid, x, y):
        self.unitid = unitid
        self.x = x
        self.y = y
        super().__init__(action, team)

class SpawnCartAction(SpawnAction):
    def __init__(self, team, unitid, x, y):
        action = Constants.ACTIONS.BUILD_CART
        self.type = UNIT_TYPES.CART
        super().__init__(action, team, unitid, x, y)

class SpawnWorkerAction(SpawnAction):
    def __init__(self, action, team, unitid, x, y):
        action = Constants.ACTIONS.BUILD_WORKER
        self.type = UNIT_TYPES.WORKER
        super().__init__(action, team, unitid, x, y)

class SpawnCityAction(Action):
    def __init__(self, team, unitid):
        action = Constants.ACTIONS.BUILD_CITY
        self.unitid = unitid
        super().__init__(action, team)

class TransferAction(Action):
    def __init__(self, team, srcID, destID, resourceType, amount):
        action = Constants.ACTIONS.TRANSFER
        self.srcID = srcID
        self.destID = destID
        self.resourceType = resourceType
        self.amount = amount
        super().__init__(action, team)

class PillageAction(Action):
    def __init__(self, team, unitid):
        action = Constants.ACTIONS.PILLAGE
        self.unitid = unitid
        super().__init__(action, team)

class ResearchAction(Action):
    def __init__(self, team, x, y):
        action = Constants.ACTIONS.RESEARCH
        self.x = x
        self.y = y
        super().__init__(action, team)

