

from unittest import TestCase
from ..game import gen
import random

class TestMap(TestCase):
    def test_gen_resources(self):
        rng = random.seed(0)
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
