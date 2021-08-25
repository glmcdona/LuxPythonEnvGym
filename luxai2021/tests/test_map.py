

from unittest import TestCase
from ..game import gen
from ..game.gen import mapSizes, SYMMETRY, generateAllResources, printMap, generateGame
import random
import math

class TestMap(TestCase):
    def test_gen_resources(self):
        print("Testing generating resource map...")
        rng = random.Random(0)
        size = mapSizes[math.floor(rng.random() * len(mapSizes))]

        halfWidth = size
        halfHeight = size
        symmetry = SYMMETRY.HORIZONTAL
        if (rng.random() < 0.5):
            symmetry = SYMMETRY.VERTICAL
            halfWidth = math.floor(size / 2)
        else:
            halfHeight = math.floor(size / 2)

        resourcesMap = generateAllResources(
            rng,
            symmetry,
            size,
            size,
            halfWidth,
            halfHeight
        )
        print("Map size %i,%i by half size symmetry %i,%i" % (size, size, halfWidth, halfHeight))

        print("Initial Resource Half Map")
        assert len(resourcesMap) == 32
        assert len(resourcesMap[0]) == 32
        print("Passed resource map generation test")
        return True

    def test_gen_game(self):
        print("Testing generating game...")
        game = generateGame(config)

        # Print the game map
        print(game.map.getMapString())



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
