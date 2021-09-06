
'''Implements /src/Actions/index.ts'''
#from .game_objects import Player, Unit, City, CityTile
from .constants import Constants

UNIT_TYPES = Constants.UNIT_TYPES

class Action:
    def __init__(self, action, team):
        self.action = action
        self.team = team
    
    def isValid(self, game):
        """
        Validates the command.
        Returns True if it's valid, False otherwise
        """
        return True
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        raise Exception("NOT IMPLEMENTED")



class MoveAction(Action):
    def __init__(self, team, unitid, direction, **kwarg):
        action = Constants.ACTIONS.MOVE
        self.unitid = unitid
        self.direction = direction
        super().__init__(action, team)
    
    def isValid(self, game):
        """
        Validates the command.
        Returns True if it's valid, False otherwise
        """
        if self.unitid == None or self.team == None or self.direction == None:
            return False

        unit = game.getUnit(self.team, self.unitid)

        # Validate it can act
        if not unit.canAct():
            return False
        
        # Check map bounds of destination spot
        newPos = unit.pos.translate(self.direction, 1)
        if newPos.y < 0 or newPos.y >= game.map.height:
            return False
        if newPos.x < 0 or newPos.x >= game.map.height:
            return False
        
        # Note: Collisions are handled in the turn loop as both players move
        return True
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        return "m {} {}".format(self.unitid, self.direction)

class SpawnAction(Action):
    def __init__(self, action, team, unitid, x, y, **kwarg):
        self.unitid = unitid
        self.x = x
        self.y = y
        super().__init__(action, team)

class SpawnCartAction(SpawnAction):
    def __init__(self, team, unitid, x, y, **kwarg):
        action = Constants.ACTIONS.BUILD_CART
        self.type = UNIT_TYPES.CART
        super().__init__(action, team, unitid, x, y)
    
    def isValid(self, game):
        """
        Validates the command.
        Returns True if it's valid, False otherwise
        """
        if self.x == None or self.y == None or self.team == None:
            return False

        citytile = game.map.getCell(self.x, self.y).citytile
        if citytile == None:
            return False
        
        if not citytile.canBuildUnit():
            return False

        # TODO handle multiple units building workers in same turn
        if game.cartUnitCapReached(self.team):
            return False
        
        return True
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        return "bc {} {}".format(self.x, self.y)

class SpawnWorkerAction(SpawnAction):
    def __init__(self, team, unitid, x, y, **kwarg):
        action = Constants.ACTIONS.BUILD_WORKER
        self.type = UNIT_TYPES.WORKER
        super().__init__(action, team, unitid, x, y)
    
    def isValid(self, game):
        """
        Validates the command.
        Returns True if it's valid, False otherwise
        """
        if self.x == None or self.y == None or self.team == None:
            return False
        
        if self.y < 0 or self.y >= game.map.height:
            return False
        if self.x < 0 or self.x >= game.map.height:
            return False

        citytile = game.map.getCell(self.x, self.y).citytile
        if citytile == None:
            return False
        
        if not citytile.canBuildUnit():
            return False

        # TODO handle multiple units building workers in same turn
        if game.workerUnitCapReached(self.team):
            return False
        
        return True
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        return "bw {} {}".format(self.x, self.y)
    

class SpawnCityAction(Action):
    def __init__(self, team, unitid, **kwarg):
        action = Constants.ACTIONS.BUILD_CITY
        self.unitid = unitid
        super().__init__(action, team)
    
    def isValid(self, game):
        """
        Validates the command.
        Returns True if it's valid, False otherwise
        """
        if self.unitid == None or self.team == None:
            return False

        unit = game.getUnit(self.team, self.unitid)

        # Validate it can act
        if not unit.canAct():
            return False
        
        if not unit.canBuild(game.map):
            return False
        
        # Validate the cell
        cell = game.map.getCellByPos(unit.pos)
        if cell.isCityTile():
            return False

        if cell.hasResource():
            return False

        # Note: Collisions are handled in the turn loop as both players move
        return True
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        return "bcity {}".format(self.unitid)

class TransferAction(Action):
    def __init__(self, team, srcID, destID, resourceType, amount):
        action = Constants.ACTIONS.TRANSFER
        self.srcID = srcID
        self.destID = destID
        self.resourceType = resourceType
        self.amount = amount
        super().__init__(action, team)
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        return "t {} {} {} {}".format(self.srcID, self.destID, self.resourceType, self.amount)

class PillageAction(Action):
    def __init__(self, team, unitid):
        action = Constants.ACTIONS.PILLAGE
        self.unitid = unitid
        super().__init__(action, team)
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        return "p {}".format(self.unitid)

class ResearchAction(Action):
    def __init__(self, team, x, y):
        action = Constants.ACTIONS.RESEARCH
        self.x = x
        self.y = y
        super().__init__(action, team)
    
    def toMessage(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized aciton message to send kaggle controller
        """
        return "r {} {}".format(self.x, self.y)

