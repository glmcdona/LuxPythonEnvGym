from .game_constants import GAME_CONSTANTS

class Constants:
    class INPUT_CONSTANTS:
        RESEARCH_POINTS = "rp"
        RESOURCES = "r"
        UNITS = "u"
        CITY = "c"
        CITY_TILES = "ct"
        ROADS = "ccd"
        DONE = "D_DONE"
    class DIRECTIONS:
        NORTH = "n"
        WEST = "w"
        SOUTH = "s"
        EAST = "e"
        CENTER = "c"
    class UNIT_TYPES:
        WORKER = 0
        CART = 1
    class TEAM:
        A = 0
        B = 1
    class RESOURCE_TYPES:
        WOOD = "wood"
        URANIUM = "uranium"
        COAL = "coal"
    class MAP_TYPES:
        EMPTY = 'empty'
        RANDOM = 'random'
        DEBUG = 'debug'

LuxMatchConfigs_Default ={
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