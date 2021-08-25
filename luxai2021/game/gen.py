'''Implements /src/Game/gen.ts'''

import random
import math
from .constants import Constants
from .game_map import GameMap, Position, Resource
from .game_objects import Player, Unit, City, CityTile, Worker, Cart

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
];


def generateGame(matchconfigs):
    configs = matchconfigs # TODO: Is this line translated right?
    seed = configs.seed
    rng = random.seed(seed)

    size = mapSizes[math.floor(rng() * mapSizes.length)]
    if (configs.width == None):
        configs.width = size
    
    if (configs.height == None):
        configs.height = size

    game = new Game(configs);
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
            halfWidth = width / 2
        else:
            halfHeight = height / 2
        
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
        deltaIndex = math.floor(rng.random()() * MOVE_DELTAS.length)
        woodSpawnsDeltas = [
            MOVE_DELTAS[deltaIndex],
            MOVE_DELTAS[(deltaIndex + 1) % MOVE_DELTAS.length],
            MOVE_DELTAS[(deltaIndex + 2) % MOVE_DELTAS.length],
            MOVE_DELTAS[(deltaIndex + 3) % MOVE_DELTAS.length],
            MOVE_DELTAS[(deltaIndex + 4) % MOVE_DELTAS.length],
            MOVE_DELTAS[(deltaIndex + 5) % MOVE_DELTAS.length],
            MOVE_DELTAS[(deltaIndex + 6) % MOVE_DELTAS.length]
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
                count += 1;
                map.addResource(nx, ny, Resource.Types.WOOD, 800)
            
            if not map.getCell(nx2, ny2).hasResource() and map.getCell(nx2, ny2).citytile == None:
                count += 1;
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
        resourcesMap.push([])
        for j in range(width):
            resourcesMap[i].push(None)

    woodResourcesMap = generateResourceMap(
        rng,
        0.21,
        0.01,
        halfWidth,
        halfHeight,
        { "deathLimit": 2, "birthLimit": 4 }
    )

    for row, y in woodResourcesMap:
        for val, x in row:
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

    for row, y in coalResourcesMap:
        for val, x in row:
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

    for row, y in uraniumResourcesMap:
        for val, x in row:
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
                    if (resource.type == 'coal'):
                        amt = 350 + math.floor(rng.random() * 75)
                    
                    if (resource.type == 'wood'):
                        amt = min(300 + math.floor(rng.random() * 100), 500)
                    
                    resourcesMap[ny][nx] = { "type": resource.type, "amt": amt }


    for y in range(halfHeight):
        for x in range(halfWidth):
            resource = resourcesMap[y][x]
            if (symmetry == SYMMETRY.VERTICAL):
                resourcesMap[y][width - x - 1] = resource
            else:
                resourcesMap[height - y - 1][x] = resource
    
    return resourcesMap



"""
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
"""