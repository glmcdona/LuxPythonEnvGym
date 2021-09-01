from .unit import Cart
from .actions import UNIT_TYPES
import math
import random
from typing import List
from .cell import Cell
from .position import Position

from .constants import Constants

DIRECTIONS = Constants.DIRECTIONS
RESOURCE_TYPES = Constants.RESOURCE_TYPES

''' Enum implemenations '''
mapSizes = [12, 16, 24, 32]

class SYMMETRY:
  HORIZONTAL = 0
  VERTICAL = 1

MOVE_DELTAS = [
  [0, 1],
  [-1, 1],
  [-1, 0],
  [-1, -1],
  [0, -1],
  [1, -1],
  [1, 0],
  [1, 1],
]

def sign(value):
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0

'''Implements /src/GameMap/index.ts'''
class GameMap:
    def __init__(self, configs):
        self.configs = configs
        self.resources = []
        self.resources_by_type = {
                                    Constants.RESOURCE_TYPES.WOOD : [],
                                    Constants.RESOURCE_TYPES.COAL : [],
                                    Constants.RESOURCE_TYPES.URANIUM : [],
                                }

    def generateMap(self, game):
        ''' Initialize the random map '''
        '''Implements /src/Game/gen.ts'''
        if self.configs["seed"] != None:
            seed = self.configs["seed"]
            rng = random.Random(seed)
        else:
            rng = random.Random()
        
        size = mapSizes[math.floor(rng.random() * len(mapSizes))]
        if ("width" not in self.configs):
            self.configs["width"] = size
        
        if ("height" not in self.configs):
            self.configs["height"] = size

        self.width = size
        self.height = size
        
        # Create map tiles
        self.map: List[List[Cell]] = [None] * self.height
        for y in range(0, self.height):
            self.map[y] = [None] * self.width
            for x in range(0, self.width):
                self.map[y][x] = Cell(x, y, self.configs)

        if (self.configs["mapType"] == Constants.MAP_TYPES.EMPTY):
            return
        else:
            symmetry = SYMMETRY.HORIZONTAL
            halfWidth = self.width
            halfHeight = self.height
            if (rng.random() < 0.5):
                symmetry = SYMMETRY.VERTICAL
                halfWidth = math.floor(self.width / 2)
            else:
                halfHeight = math.floor(self.height / 2)
            
            resourcesMap = self._generateAllResources(
                rng,
                symmetry,
                self.width,
                self.height,
                halfWidth,
                halfHeight
            )

            retries = 0
            while (not self._validateResourcesMap(resourcesMap)):
                retries += 1
                resourcesMap = self._generateAllResources(
                    rng,
                    symmetry,
                    self.width,
                    self.height,
                    halfWidth,
                    halfHeight
                )
            
            for y, row in enumerate(resourcesMap):
                for x, val in enumerate(row):
                    if (val != None):
                        self.addResource(x, y, val["type"], val["amt"])

            spawnX = math.floor(rng.random() * (halfWidth - 1)) + 1
            spawnY = math.floor(rng.random() * (halfHeight - 1)) + 1
            while (self.getCell(spawnX, spawnY).hasResource()):
                spawnX = math.floor(rng.random() * (halfWidth - 1)) + 1
                spawnY = math.floor(rng.random() * (halfHeight - 1)) + 1
            
            game.spawnWorker(Constants.TEAM.A, spawnX, spawnY)
            game.spawnCityTile(Constants.TEAM.A, spawnX, spawnY)
            if (symmetry == SYMMETRY.HORIZONTAL):
                game.spawnWorker(Constants.TEAM.B, spawnX, self.height - spawnY - 1)
                game.spawnCityTile(Constants.TEAM.B, spawnX, self.height - spawnY - 1)
            else:
                game.spawnWorker(Constants.TEAM.B, self.width - spawnX - 1, spawnY)
                game.spawnCityTile(Constants.TEAM.B, self.width - spawnX - 1, spawnY)
            
            # add at least 3 wood deposits near spawns
            deltaIndex = math.floor(rng.random() * len(MOVE_DELTAS))
            woodSpawnsDeltas = [
                MOVE_DELTAS[deltaIndex],
                MOVE_DELTAS[(deltaIndex + 1) % len(MOVE_DELTAS)],
                MOVE_DELTAS[(deltaIndex + 2) % len(MOVE_DELTAS)],
                MOVE_DELTAS[(deltaIndex + 3) % len(MOVE_DELTAS)],
                MOVE_DELTAS[(deltaIndex + 4) % len(MOVE_DELTAS)],
                MOVE_DELTAS[(deltaIndex + 5) % len(MOVE_DELTAS)],
                MOVE_DELTAS[(deltaIndex + 6) % len(MOVE_DELTAS)]
            ]
            count = 0
            for delta in woodSpawnsDeltas:
                nx = spawnX + delta[0]
                ny = spawnY + delta[1]
                nx2 = nx
                ny2 = ny
                if (symmetry == SYMMETRY.HORIZONTAL):
                    ny2 = self.height - ny - 1
                else:
                    nx2 = self.width - nx - 1
                
                if not self.inMap(Position(nx, ny)) or not self.inMap(Position(nx2, ny2)):
                    continue
                
                if not self.getCell(nx, ny).hasResource() and self.getCell(nx, ny).citytile == None:
                    count += 1
                    self.addResource(nx, ny, Constants.RESOURCE_TYPES.WOOD, 800)
                
                if not self.getCell(nx2, ny2).hasResource() and self.getCell(nx2, ny2).citytile == None:
                    count += 1
                    self.addResource(nx2, ny2, Constants.RESOURCE_TYPES.WOOD, 800)
                
                if (count == 6): break

            return

    def _validateResourcesMap(self, resourcesMap):
        data = { "wood": 0, "coal": 0, "uranium": 0 }
        for y, row in enumerate(resourcesMap):
            for x, val in enumerate(row):
                if (val != None):
                    data[resourcesMap[y][x]["type"]] += resourcesMap[y][x]["amt"]
        
        if (data["wood"] < 2000):
            return False
        if (data["coal"] < 1500):
            return False
        if (data["uranium"] < 300):
            return False
        return True

    def _generateAllResources(self, rng, symmetry, width, height, halfWidth, halfHeight):
        resourcesMap = []

        for i in range(height):
            resourcesMap.append([])
            for j in range(width):
                resourcesMap[i].append(None)

        woodResourcesMap = self._generateResourceMap(
            rng,
            0.21,
            0.01,
            halfWidth,
            halfHeight,
            { "deathLimit": 2, "birthLimit": 4 }
        )

        for y, row in enumerate(woodResourcesMap):
            for x, val in enumerate(row):
                if (val == 1):
                    amt = min(300 + math.floor(rng.random() * 100), 500)
                    resourcesMap[y][x] = { "type": Constants.RESOURCE_TYPES.WOOD, "amt": amt }
        
        coalResourcesMap = self._generateResourceMap(
            rng,
            0.11,
            0.02,
            halfWidth,
            halfHeight,
            { "deathLimit": 2, "birthLimit": 4 }
        )

        for y, row in enumerate(coalResourcesMap):
            for x, val in enumerate(row):
                if (val == 1):
                    amt = 350 + math.floor(rng.random() * 75)
                    resourcesMap[y][x] = { "type": Constants.RESOURCE_TYPES.COAL, "amt": amt }

        uraniumResourcesMap = self._generateResourceMap(
            rng,
            0.055,
            0.04,
            halfWidth,
            halfHeight,
            { "deathLimit": 1, "birthLimit": 6 }
        )

        for y, row in enumerate(uraniumResourcesMap):
            for x, val in enumerate(row):
                if (val == 1):
                    amt = 300 + math.floor(rng.random() * 50)
                    resourcesMap[y][x] = { "type": Constants.RESOURCE_TYPES.URANIUM, "amt": amt }
        

        for i in range(10):
            resourcesMap = self._gravitateResources(resourcesMap);
        
        # perturb resources
        for y in range(halfHeight):
            for x in range(halfWidth):
                resource = resourcesMap[y][x]
                if (resource == None): continue
                for d in MOVE_DELTAS:
                    nx = x + d[0]
                    ny = y + d[1]
                    if (nx < 0 or ny < 0 or nx >= halfHeight or ny >= halfWidth): continue
                    if (rng.random() < 0.05):
                        amt = 300 + math.floor(rng.random() * 50)
                        if (resource["type"] == 'coal'):
                            amt = 350 + math.floor(rng.random() * 75)
                        
                        if (resource["type"] == 'wood'):
                            amt = min(300 + math.floor(rng.random() * 100), 500)
                        
                        resourcesMap[ny][nx] = { "type": resource["type"], "amt": amt }


        for y in range(halfHeight):
            for x in range(halfWidth):
                resource = resourcesMap[y][x]
                if (symmetry == SYMMETRY.VERTICAL):
                    resourcesMap[y][width - x - 1] = resource
                else:
                    resourcesMap[height - y - 1][x] = resource
        
        return resourcesMap

    def _generateResourceMap(self, rng, density, densityRange, width, height, golOptions = { "deathLimit": 2, "birthLimit": 4 } ):
        # width, height should represent half of the map
        DENSITY = density - densityRange / 2 + densityRange * rng.random();
        arr = []
        for y in range(height):
            arr.append([])
            for x in range(width):
                type = 0
                if (rng.random() < DENSITY):
                    type = 1

                arr[y].append(type)

        # simulate GOL for 2 rounds
        for i in range(2):
            arr = self._simulateGOL(arr, golOptions)
        
        return arr

    def _simulateGOL(self, arr, options):
        # high birthlimit = unlikely to deviate from initial random spots
        # high deathlimit = lots of patches die
        padding = 1
        deathLimit = options["deathLimit"]
        birthLimit = options["birthLimit"]
        for i in range( padding, len(arr) - padding ):
            for j in range( padding, len(arr[0]) - padding ):
                alive = 0
                for k in range( len(MOVE_DELTAS) ):
                    delta = MOVE_DELTAS[k]
                    ny = i + delta[1]
                    nx = j + delta[0]
                    if (arr[ny][nx] == 1):
                        alive += 1
                
                if (arr[i][j] == 1):
                    if (alive < deathLimit):
                        arr[i][j] = 0
                    else:
                        arr[i][j] = 1
                else:
                    if (alive > birthLimit):
                        arr[i][j] = 1
                    else:
                        arr[i][j] = 0
        
        return arr


    def _kernelForce(self, resourcesMap, rx, ry):
        force = [0, 0]
        resource = resourcesMap[ry][rx]
        kernelSize = 5

        for y in range(ry - kernelSize, ry + kernelSize):
            for x in range(rx - kernelSize, rx + kernelSize):
                if (x < 0 or y < 0 or x >= len(resourcesMap[0]) or y >= len(resourcesMap)): continue

                r2 = resourcesMap[y][x]
                if (r2 != None):
                    dx = rx - x
                    dy = ry - y
                    mdist = abs(dx) + abs(dy)
                    if (r2["type"] != resource["type"]):
                        if (dx != 0): force[0] += math.pow(dx/mdist, 2) * sign(dx)
                        if (dy != 0): force[1] += math.pow(dy/mdist, 2) * sign(dy)
                    else:
                        if (dx != 0): force[0] -= math.pow(dx/mdist, 2) * sign(dx)
                        if (dy != 0): force[1] -= math.pow(dy/mdist, 2) * sign(dy)
        
        return force


    def _gravitateResources(self, resourcesMap):
        #
        # Gravitate like to like, push different resources away from each other.
        # 
        # Add's a force direction to each cell.
        #
        newResourcesMap = []
        for y in range(len(resourcesMap)):
            newResourcesMap.append([])
            for x in range(len(resourcesMap[y])):
                newResourcesMap[y].append(None)
                res = resourcesMap[y][x]
                if (res != None):
                    f = self._kernelForce(resourcesMap, x, y)
                    resourcesMap[y][x]["force"] = f

        for y in range(len(resourcesMap)):
            for x in range(len(resourcesMap[y])):
                res = resourcesMap[y][x]
                if (res != None):
                    nx = x + sign(res["force"][0])*1
                    ny = y + sign(res["force"][1])*1
                    if (nx < 0): nx = 0
                    if (ny < 0): ny = 0
                    if (nx >= len(resourcesMap[0])): nx = len(resourcesMap[0])-1
                    if (ny >= len(resourcesMap)): ny = len(resourcesMap) - 1
                    if (newResourcesMap[ny][nx] == None):
                        newResourcesMap[ny][nx] = res
                    else:
                        newResourcesMap[y][x] = res
        
        return newResourcesMap

    def addResource(self, x, y, resourceType, amount):
        cell = self.getCell(x, y)
        cell.setResource(resourceType, amount)
        self.resources.append(cell)
        self.resources_by_type[resourceType].append(cell)
        return cell

    def getCellByPos(self, pos) -> Cell:
        if pos.y >= len(self.map) or pos.x >= len(self.map[0]) or pos.y < 0 or pos.x < 0:
            return None
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
        map_str = ''
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
                        
                        map_str += unitstr
                    else:
                        unitstr = str(len(cell.units))
                        
                        if unit.team == Constants.TEAM.A:
                            unitstr += "a"
                        elif unit.team == Constants.TEAM.B:
                            unitstr += "b"
                        else:
                            unitstr += "?"
                        
                        map_str += unitstr
                elif (cell.hasResource()):
                    if cell.resource.type == Constants.RESOURCE_TYPES.WOOD:
                        map_str += "w,"
                    if cell.resource.type == Constants.RESOURCE_TYPES.COAL:
                        map_str += "c,"
                    if cell.resource.type == Constants.RESOURCE_TYPES.URANIUM:
                        map_str += "u,"
                elif (cell.isCityTile()):
                        map_str += "C";
                        if cell.citytile.team == Constants.TEAM.A:
                            map_str += "a"
                        elif cell.citytile.team == Constants.TEAM.B:
                            map_str += "b"
                        else:
                            map_str += "?"
                else:
                    map_str += ".."
            map_str += "\n"
        return map_str


