'''Implements /src/GameMap/cell.ts'''

from .position import Position
from .resource import Resource
from .game_objects import CityTile

'''
/**
 * Cell class for map cells
 *
 * Some restrictions not explicitly employed:
 * Cell can either be empty (no resource or citytile), or have a resource, or have a citytile, not multiple.
 * There may be multiple units but this is only allowed on city tiles
 */
 '''
class Cell:
    def __init__(self, x, y, configs):
        self.pos = Position(x, y)
        self.resource: Resource = None
        self.citytile = None
        self.configs = configs
        self.road = configs.parameters.MIN_ROAD

    def setResource(self, resourceType, amount):
        self.resource = Resource(resourceType, amount)

    def hasResource(self):
        return self.resource is not None and self.resource.amount > 0
    
    def setCityTile(self, team, cityid):
        self.citytile = CityTile(team, self.configs)
        self.citytile.pos = self.pos
        self.citytile.cityid = cityid
    
    def isCityTile(self):
        return self.citytile != None
    
    def hasUnits(self):
        return self.units.size != 0
    
    def getRoad(self):
        if self.isCityTile():
            return self.configs.parameters.MAX_ROAD
        else:
            return self.road
    
    
    
