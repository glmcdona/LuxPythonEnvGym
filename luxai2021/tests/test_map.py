

from luxai2021.game.actions import MoveAction
from unittest import TestCase

import random
import math
from ..game.game import Game
from ..game.constants import Constants, LuxMatchConfigs_Default
from ..game.game_constants import GAME_CONSTANTS


class TestMap(TestCase):
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

        game = Game(LuxMatchConfigs)

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

        game = Game(LuxMatchConfigs)

        # Print the game map
        print("Map for seed 123456789:")
        print(game.map.getMapString())

        # Test units
        units = list(game.getTeamsUnits(Constants.TEAM.A).values())
        assert len(units) == 1

        # Try moving a unit, not a great test since maybe can't move North and
        # opponent may be beside this unit.
        test = {}
        unit = units[0]
        oldCellPosition = game.map.getCellByPos( unit.pos )
        newCellPosition = game.map.getCellByPos(
                unit.pos.translate(Constants.DIRECTIONS.NORTH, 1)
            )
        action = MoveAction(
            Constants.TEAM.A,
            unit.id,
            Constants.DIRECTIONS.NORTH
        )

        # Move the unit and run a single turn
        assert len(oldCellPosition.units) == 1
        assert len(newCellPosition.units) == 0
        print(unit.cargo)
        assert unit.cargo[Constants.RESOURCE_TYPES.WOOD] == 0

        gameOver = game.runTurnWithActions([action])

        print(game.map.getMapString())
        assert gameOver == False
        assert len(oldCellPosition.units) == 0
        assert len(newCellPosition.units) == 1
        print(unit.cargo)
        assert unit.cargo[Constants.RESOURCE_TYPES.WOOD] == 60

        # Let the game run it's course
        while not gameOver:
            gameOver = game.runTurnWithActions([])
        print(game.map.getMapString())

        return True

