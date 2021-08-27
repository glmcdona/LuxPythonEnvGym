

from unittest import TestCase
from ..game import gen
from ..game.gen import mapSizes, SYMMETRY, generateAllResources, printMap, generateGame
import random
import math
from ..game.constants import Constants, LuxMatchConfigs_Default
from ..game.game_constants import GAME_CONSTANTS


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
        printMap(resourcesMap)
        assert len(resourcesMap) == 32
        assert len(resourcesMap[0]) == 32
        print("Passed resource map generation test!")
        return True

    def test_gen_game(self):
        print("Testing generating game...")
        LuxMatchConfigs = {
            "mapType": Constants.MAP_TYPES.RANDOM,
            "storeReplay": True,
            "seed": None,
            "debug": False,
            "debugDelay": 500,
            "runProfiler": False,
            "compressReplay": False,
            "debugAnnotations": False,
            "statefulReplay": False,
            "parameters": GAME_CONSTANTS["PARAMETERS"],
        }

        game = generateGame(LuxMatchConfigs)

        # Print the game map
        print(game.map.getMapString())
        print("Map shape: %i,%i" % ( len(game.map.map), len(game.map.map[0])))
        assert len(game.map.map) >= 5
        assert len(game.map.map[0]) >= 5
        assert len(game.cities) == 2
        
        # Print game stats
        print(game.stats)
        assert game.stats["teamStats"][0]["workersBuilt"] == 1

        # Print game state
        print(game.state)
        assert len(game.state["teamStates"][0]["units"]) == 1

        print("Passed game creation test!")
        return True

    def test_gen_game_seed(self):
        print("Testing generating specific game...")
        LuxMatchConfigs = {
            "mapType": Constants.MAP_TYPES.RANDOM,
            "storeReplay": True,
            "seed": 123456789,
            "debug": False,
            "debugDelay": 500,
            "runProfiler": False,
            "compressReplay": False,
            "debugAnnotations": False,
            "statefulReplay": False,
            "parameters": GAME_CONSTANTS["PARAMETERS"],
        }

        game = generateGame(LuxMatchConfigs)

        # Print the game map
        print("Map for seed 123456789:")
        print(game.map.getMapString())
        return True

