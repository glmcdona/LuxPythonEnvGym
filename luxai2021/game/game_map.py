import math
import random
from typing import List
from .cell import Cell

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES



'''Implements /src/GameMap/index.ts'''
class GameMap:

    ''' Implements the Enums. '''
    class Types:
        EMPTY = 'empty'
        RANDOM = 'random'
        DEBUG = 'debug'


    def __init__(self, configs):
        self.height = configs.height
        self.width = configs.width

        # Create map tiles
        self.map: List[List[Cell]] = [None] * self.height
        for y in range(0, self.height):
            self.map[y] = [None] * self.width
            for x in range(0, self.width):
                self.map[y][x] = Cell(x, y)

    def addResource(self, x, y, resourceType, amount):
        cell = self.getCell(x, y)
        cell.setResource(resourceType, amount)
        self.resources.push(cell)
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
            cells.push(self.getCell(cell.pos.x, cell.pos.y - 1))
        
        # EAST
        if cell.pos.x < self.width - 1:
            cells.push(self.getCell(cell.pos.x + 1, cell.pos.y))
        
        # SOUTH
        if cell.pos.y < self.height - 1:
            cells.push(self.getCell(cell.pos.x, cell.pos.y + 1))
        
        # WEST
        if cell.pos.x > 0:
            cells.push(self.getCell(cell.pos.x - 1, cell.pos.y))
        
        return cells
    
    def inMap(self, pos):
        return not (pos.x < 0 or pos.y < 0 or pos.x >= self.width or pos.y >= self.height )
    

    '''
    * Return printable map string
    '''
    def getMapString(self):
        #TODO: Optionally implement this to print the game as text
        return ""


