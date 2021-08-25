import math
import random
from typing import List
from .cell import Cell

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from .game_objects import Player, Unit, City, CityTile

class Resource:
    def __init__(self, r_type: str, amount: int):
        self.type = r_type
        self.amount = amount


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


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, pos) -> int:
        return abs(pos.x - self.x) + abs(pos.y - self.y)

    def distanceTo(self, pos):
        """
        Returns Manhattan (L1/grid) distance to pos
        """
        return self - pos

    def isAdjacent(self, pos):
        return (self - pos) <= 1

    def __eq__(self, pos) -> bool:
        return self.x == pos.x and self.y == pos.y

    def equals(self, pos):
        return self == pos

    def translate(self, direction, units) -> 'Position':
        if direction == DIRECTIONS.NORTH:
            return Position(self.x, self.y - units)
        elif direction == DIRECTIONS.EAST:
            return Position(self.x + units, self.y)
        elif direction == DIRECTIONS.SOUTH:
            return Position(self.x, self.y + units)
        elif direction == DIRECTIONS.WEST:
            return Position(self.x - units, self.y)
        elif direction == DIRECTIONS.CENTER:
            return Position(self.x, self.y)

    def directionTo(self, target_pos: 'Position') -> DIRECTIONS:
        """
        Return closest position to target_pos from this position
        """
        check_dirs = [
            DIRECTIONS.NORTH,
            DIRECTIONS.EAST,
            DIRECTIONS.SOUTH,
            DIRECTIONS.WEST,
        ]
        closest_dist = self.distanceTo(target_pos)
        closest_dir = DIRECTIONS.CENTER
        for direction in check_dirs:
            newpos = self.translate(direction, 1)
            dist = target_pos.distanceTo(newpos)
            if dist < closest_dist:
                closest_dir = direction
                closest_dist = dist
        return closest_dir

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
