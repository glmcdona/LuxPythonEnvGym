from .constants import Constants
from .game_map import GameMap
from .game_objects import Player, Unit, City, CityTile

INPUT_CONSTANTS = Constants.INPUT_CONSTANTS

# TODO: Add all the game logic here!
class Game:
    def _initialize(self, messages):
        """
        initialize state
        """
        self.id = int(messages[0])
        self.turn = -1
        # get some other necessary initial input
        mapInfo = messages[1].split(" ")
        self.map_width = int(mapInfo[0])
        self.map_height = int(mapInfo[1])
        self.map = GameMap(self.map_width, self.map_height)
        self.players = [Player(0), Player(1)]

    def _end_turn(self):
        print("D_FINISH")

    def _reset_player_states(self):
        self.players[0].units = []
        self.players[0].cities = {}
        self.players[0].city_tile_count = 0
        self.players[1].units = []
        self.players[1].cities = {}
        self.players[1].city_tile_count = 0

    def step_unit(self):
        """
        Run the game simulation for a single unit.
        """
        # TODO: Implement single step of a unit
        pass

    def step(self):
        """
        Run the game simulation for a full turn
        """
        # TODO: Implement single step of a unit
        pass