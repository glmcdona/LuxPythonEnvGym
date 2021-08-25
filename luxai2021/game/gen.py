'''Implements /src/Game/gen.ts'''

import random
import math
from .constants import Constants
from .game import Game
from .position import Position
from .resource import Resource
from .game_map import GameMap
from .unit import Unit, Worker, Cart
from .game_objects import City

mapSizes = [12, 16, 24, 32];

''' Enum implemenations '''
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

def generateGame(matchconfigs):
    configs = matchconfigs # TODO: Is this line translated right?
    seed = configs.seed
    rng = random.Random(seed)

    size = mapSizes[math.floor(rng.random() * len(mapSizes))]
    if (configs.width == None):
        configs.width = size
    
    if (configs.height == None):
        configs.height = size

    game = Game(configs)
    map = game.map
    width = map.width
    height = map.height

    if (configs.mapType == GameMap.Types.EMPTY):
        return game
    else:
        symmetry = SYMMETRY.HORIZONTAL
        halfWidth = width
        halfHeight = height
        if (rng.random() < 0.5):
            symmetry = SYMMETRY.VERTICAL
            halfWidth = math.floor(width / 2)
        else:
            halfHeight = math.floor(height / 2)
        
        resourcesMap = generateAllResources(
            rng,
            symmetry,
            width,
            height,
            halfWidth,
            halfHeight
        )

        retries = 0
        while (not validateResourcesMap(resourcesMap)):
            retries += 1
            resourcesMap = generateAllResources(
                rng,
                symmetry,
                width,
                height,
                halfWidth,
                halfHeight
            )
        
        for row, y in resourcesMap.Items():
            for val, x in row:
                if (val != None):
                    map.addResource(x, y, val["type"], val["amt"])

        spawnX = math.floor(rng.random()() * (halfWidth - 1)) + 1
        spawnY = math.floor(rng.random()() * (halfHeight - 1)) + 1
        while (map.getCell(spawnX, spawnY).hasResource()):
            spawnX = math.floor(rng.random()() * (halfWidth - 1)) + 1
            spawnY = math.floor(rng.random()() * (halfHeight - 1)) + 1
        
        game.spawnWorker(Unit.TEAM.A, spawnX, spawnY)
        game.spawnCityTile(Unit.TEAM.A, spawnX, spawnY)
        if (symmetry == SYMMETRY.HORIZONTAL):
            game.spawnWorker(Unit.TEAM.B, spawnX, height - spawnY - 1)
            game.spawnCityTile(Unit.TEAM.B, spawnX, height - spawnY - 1)
        else:
            game.spawnWorker(Unit.TEAM.B, width - spawnX - 1, spawnY)
            game.spawnCityTile(Unit.TEAM.B, width - spawnX - 1, spawnY)
        
        # add at least 3 wood deposits near spawns
        deltaIndex = math.floor(rng.random()() * len(MOVE_DELTAS))
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
                ny2 = height - ny - 1
            else:
                nx2 = width - nx - 1
            
            if not map.inMap(Position(nx, ny)) or not map.inMap(Position(nx2, ny2)):
                continue
            
            if not map.getCell(nx, ny).hasResource() and map.getCell(nx, ny).citytile == None:
                count += 1
                map.addResource(nx, ny, Resource.Types.WOOD, 800)
            
            if not map.getCell(nx2, ny2).hasResource() and map.getCell(nx2, ny2).citytile == None:
                count += 1
                map.addResource(nx2, ny2, Resource.Types.WOOD, 800)
            
            if (count == 6): break

        return game


def validateResourcesMap(resourcesMap):
    data = { "wood": 0, "coal": 0, "uranium": 0 }
    for row, y in resourcesMap:
        for val, x in row:
            if (val != None):
                data[resourcesMap[y][x]["type"]] += resourcesMap[y][x]["amt"]
    
    if (data["wood"] < 2000):
        return False
    if (data["coal"] < 1500):
        return False
    if (data["uranium"] < 300):
        return False
    return True

def generateAllResources(rng, symmetry, width, height, halfWidth, halfHeight):
    resourcesMap = []

    for i in range(height):
        resourcesMap.append([])
        for j in range(width):
            resourcesMap[i].append(None)

    woodResourcesMap = generateResourceMap(
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
                resourcesMap[y][x] = { "type": Resource.Types.WOOD, "amt": amt }
    
    coalResourcesMap = generateResourceMap(
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
                resourcesMap[y][x] = { "type": Resource.Types.COAL, "amt": amt }

    uraniumResourcesMap = generateResourceMap(
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
                resourcesMap[y][x] = { "type": Resource.Types.URANIUM, "amt": amt }
    

    for i in range(10):
        resourcesMap = gravitateResources(resourcesMap);
    
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

def generateResourceMap(rng, density, densityRange, width, height, golOptions = { "deathLimit": 2, "birthLimit": 4 } ):
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
        arr = simulateGOL(arr, golOptions)
    
    return arr

def simulateGOL(arr, options):
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


def kernelForce(resourcesMap, rx, ry):
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


def gravitateResources(resourcesMap):
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
                f = kernelForce(resourcesMap, x, y)
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


def printMap(resourcesMap):
    str = ''
    for y in range(len(resourcesMap)):
        for x in range(len(resourcesMap[y])):
            res = resourcesMap[y][x]
            if (res == None):
                str += "0 "
            else:
                str += "%s " % (res["type"][0])
        str += "\n"
    
    print(str)


'''
rng = random.random(0)
size = mapSizes[math.floor(rng.random() * len(mapSizes))]

halfWidth = size
halfHeight = size
symmetry = SYMMETRY.HORIZONTAL
if (rng() < 0.5):
   symmetry = SYMMETRY.VERTICAL
   halfWidth = size / 2
else:
    halfHeight = size / 2

resourcesMap = generateAllResources(
   rng,
   symmetry,
   size,
   size,
   halfWidth,
   halfHeight
 )

print("Initial Resource Half Map")
printMap(resourcesMap)
'''
