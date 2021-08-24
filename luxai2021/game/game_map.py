import math
import random
from typing import List
from cell import Cell

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

from .game_objects import Player, Unit, City, CityTile

class Resource:
    def __init__(self, r_type: str, amount: int):
        self.type = r_type
        self.amount = amount



class GameMap:
    def __init__(self, game, width, height):
        self.game = game
        self.height = height
        self.width = width

        # Create map tiles
        self.map: List[List[Cell]] = [None] * height
        for y in range(0, self.height):
            self.map[y] = [None] * width
            for x in range(0, self.width):
                self.map[y][x] = Cell(x, y)

        # Initialize the units and resources on the map
        self._generateMap()
        
    def _generateMap(self):
        '''
        Generate the symmetric random map
        Mirror of /Lux-Design-2021/blob/master/src/logic.ts initialize()->generateGame()
        '''
        seed = random.randint()

        # Generate only part of the map, and apply symettricaly
        symmetry_horizontal = (random.random() <= 0.5)
        half_height = self.height
        half_width = self.width
        if symmetry_horizontal:
            half_height = half_height / 2
        else:
            half_width = half_width / 2

        # DEBUG: Generate some random resources around the map.
        # TODO: Replace with proper symettric map generation after Stone finishes revamp of official generation.
        for x in range(half_height):
            for y in range(half_width):
                if random.rand()  <= 0.10:
                    self.map[y][x].resource = Resource(Constants.RESOURCE_TYPES.WOOD, 400)
                elif random.rand() <= 0.03:
                    self.map[y][x].resource = Resource(Constants.RESOURCE_TYPES.COAL, 100)
                elif random.rand() <= 0.015:
                    self.map[y][x].resource = Resource(Constants.RESOURCE_TYPES.URANIUM, 20)

        # Place the starting cities and workers
        self.game.spawnCityTile(Unit.TEAM.A, 2, 1);
        self.game.spawnCityTile(Unit.TEAM.B, self.width - 3, 1);

        self.game.spawnWorker(Unit.TEAM.A, 2, 2);
        self.game.spawnWorker(Unit.TEAM.B, self.width - 3, 2);


    def getCellByPos(self, pos) -> Cell:
        return self.map[pos.y][pos.x]

    def getCell(self, x, y) -> Cell:
        return self.map[y][x]

    def _setResource(self, r_type, x, y, amount):
        """
        do not use this function, this is for internal tracking of state
        """
        cell = self.getCell(x, y)
        cell.resource = Resource(r_type, amount)


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
