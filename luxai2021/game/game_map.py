from .unit import Cart
from .actions import UNIT_TYPES
import math
import random
from typing import List
from .cell import Cell

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES



'''Implements /src/GameMap/index.ts'''
class GameMap:
    def __init__(self, configs):
        self.height = configs["height"]
        self.width = configs["width"]
        self.resources = []
        self.resources_by_type = {
                                    Constants.RESOURCE_TYPES.WOOD : [],
                                    Constants.RESOURCE_TYPES.COAL : [],
                                    Constants.RESOURCE_TYPES.URANIUM : [],
                                }

        # Create map tiles
        self.map: List[List[Cell]] = [None] * self.height
        for y in range(0, self.height):
            self.map[y] = [None] * self.width
            for x in range(0, self.width):
                self.map[y][x] = Cell(x, y, configs)

    def addResource(self, x, y, resourceType, amount):
        cell = self.getCell(x, y)
        cell.setResource(resourceType, amount)
        self.resources.append(cell)
        self.resources_by_type[resourceType].append(cell)
        return cell

    def getCellByPos(self, pos) -> Cell:
        return self.map[pos.y][pos.x]

    def getCell(self, x, y) -> Cell:
        return self.map[y][x]
    
    def getRow(self, y):
        return self.map[y]
    
    def getAdjacentCells(self, cell):
        cells = []

        # NORTH
        if cell.pos.y > 0:
            cells.append(self.getCell(cell.pos.x, cell.pos.y - 1))
        
        # EAST
        if cell.pos.x < self.width - 1:
            cells.append(self.getCell(cell.pos.x + 1, cell.pos.y))
        
        # SOUTH
        if cell.pos.y < self.height - 1:
            cells.append(self.getCell(cell.pos.x, cell.pos.y + 1))
        
        # WEST
        if cell.pos.x > 0:
            cells.append(self.getCell(cell.pos.x - 1, cell.pos.y))
        
        return cells
    
    def inMap(self, pos):
        return not (pos.x < 0 or pos.y < 0 or pos.x >= self.width or pos.y >= self.height )
    

    '''
    * Return printable map string
    '''
    def getMapString(self):
        # W<team> = Worker
        # C<team> = Cart
        # ◰<team> = City
        # <number><team> = Stacked units from specified team.
        # ▩▩ = Wood
        # ▣▣ = Coal
        # ▷▷ == Uranium
        str = ''
        for y in range(self.height):
            row = self.getRow(y)
            for cell in row:
                if (cell.hasUnits()):
                    if (len(cell.units) == 1):
                        unitstr = '?'
                        unit = list(cell.units.values())[0]
                        if unit.type == Constants.UNIT_TYPES.CART:
                            unitstr = 'c'
                        elif unit.type == Constants.UNIT_TYPES.WORKER:
                            unitstr = 'W'
                        
                        if unit.team == Constants.TEAM.A:
                            unitstr += "a"
                        elif unit.team == Constants.TEAM.B:
                            unitstr += "b"
                        else:
                            unitstr += "?"
                        
                        str += unitstr
                    else:
                        unitstr = str(len(cell.units))
                        
                        if unit.team == Constants.TEAM.A:
                            unitstr += "a"
                        elif unit.team == Constants.TEAM.B:
                            unitstr += "b"
                        else:
                            unitstr += "?"
                        
                        str += unitstr
                elif (cell.hasResource()):
                    if cell.resource.type == Constants.RESOURCE_TYPES.WOOD:
                        str += "w,"
                    if cell.resource.type == Constants.RESOURCE_TYPES.COAL:
                        str += "c,"
                    if cell.resource.type == Constants.RESOURCE_TYPES.URANIUM:
                        str += "u,"
                elif (cell.isCityTile()):
                        str += "C";
                        if cell.citytile.team == Constants.TEAM.A:
                            str += "a"
                        elif cell.citytile.team == Constants.TEAM.B:
                            str += "b"
                        else:
                            str += "?"
                else:
                    str += ".."
            str += "\n"
        return str


