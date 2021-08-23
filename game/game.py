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
        self.map = GameMap(self, self.map_width, self.map_height)
        self.players = [Player(0), Player(1)]

        # Initializations from src/Game/index.ts -> Game()
        self.global_cityid_count = 0
        self.global_unitid_count = 0
        self.cities = {} # string -> City
        self.stats = {
            "teamStats": {
                Unit.TEAM.A: {
                    "fuelGenerated": 0,
                    "resourcesCollected": {
                        "wood": 0,
                        "coal": 0,
                        "uranium": 0,
                    },
                    "cityTilesBuilt": 0,
                    "workersBuilt": 0,
                    "cartsBuilt": 0,
                    "roadsBuilt": 0,
                    "roadsPillaged": 0,
                },
                Unit.TEAM.B: {
                    "fuelGenerated": 0,
                    "resourcesCollected": {
                        "wood": 0,
                        "coal": 0,
                        "uranium": 0,
                    },
                    "cityTilesBuilt": 0,
                    "workersBuilt": 0,
                    "cartsBuilt": 0,
                    "roadsBuilt": 0,
                    "roadsPillaged": 0,
                },
            },
        }
        self.state = {
            "turn" : 0,
            "teamStates" : {
                Unit.TEAM.A : {
                    "researchPoints": 0,
                    "units" : {},
                    "researched" : {
                        "wood" : True,
                        "coal" : False,
                        "uranium" : False,
                    }
                },
                Unit.TEAM.B : {
                    "researchPoints": 0,
                    "units" : {},
                    "researched" : {
                        "wood" : True,
                        "coal" : False,
                        "uranium" : False,
                    }
                },
            }
        }

    def _gen_initial_accumulated_action_stats(self):
        """
        Initial stats
        Implements src/Game/index.ts -> Game._genInitialAccumulatedActionStats()
        """
        return {
                Unit.TEAM.A: {
                    "workersBuilt": 0,
                    "cartsBuilt": 0,
                    "actionsPlaced": set(),
                },
                Unit.TEAM.B: {
                    "workersBuilt": 0,
                    "cartsBuilt": 0,
                    "actionsPlaced": set(),
                },
            }
    
    def validate_command(self, cmd, accumulated_action_stats=None):
        """
        Returns an Action object if validated. If invalid, throws MatchWarn
        Implements src/Game/index.ts -> Game.validateCommand()
        """
        if accumulated_action_stats is None:
            accumulated_action_stats = self._gen_initial_accumulated_action_stats()
        
        # TODO: Implement
        pass

    def worker_unit_cap_reached(self, team, offset = 0):
        """
        Returns True if unit cap reached
        Implements src/Game/index.ts -> Game.workerUnitCapReached()
        """
        # TODO: Implement
        pass
    
    def cart_unit_cap_reached(self, team, offset = 0):
        """
        Returns True if unit cap reached
        Implements src/Game/index.ts -> Game.cartUnitCapReached()
        """
        # TODO: Implement
        pass
    
    def spawn_worker(self, team, x, y, unitid = None):
        """
        Spawns new worker
        Implements src/Game/index.ts -> Game.spawnWorker()
        """
        # TODO: Implement
        pass

    def spawn_cart(self, team, x, y, unitid = None):
        """
        Spawns new cart
        Implements src/Game/index.ts -> Game.spawnCart()
        """
        # TODO: Implement
        pass

    def spawn_city_tile(self, team, x, y, cityid = None):
        """
        Spawns new city tile
        Implements src/Game/index.ts -> Game.spawnCityTile()
        """
        # TODO: Implement
        pass

    def move_unit(self, team, unitid, direction):
        """
        Moves a unit
        Implements src/Game/index.ts -> Game.moveUnit()
        """
        # TODO: Implement
        pass

    def handle_resource_release(self, original_cell):
        """
        For cells with resources, this will release the resource to all adjacent workers (including any unit on top)
        Implements src/Game/index.ts -> Game.handleResourceRelease()
        """
        # TODO: Implement
        pass
    
    def handle_resource_deposit(self, unit):
        """
        Auto deposit resources of unit to tile it is on
        Implements src/Game/index.ts -> Game.handleResourceDeposit()
        """
        # TODO: Implement
        pass

    def get_teams_units(self, team):
        """
        Get list of units.
        Implements src/Game/index.ts -> Game.getTeamsUnits()
        """
        # TODO: Implement
        pass

    def get_unit(self, team, unitid):
        """
        Get the specific unit.
        Implements src/Game/index.ts -> Game.getUnit()
        """
        # TODO: Implement
        pass
    
    def transfer_resources(self, team, src_unitid, dest_unitid, resource_type, amount):
        """
        Transfer resouces on a given team between 2 units. This does not check adjacency requirement, but its expected
        that the 2 units are adjacent. This allows for simultaneous movement of 1 unit and transfer of another
        Implements src/Game/index.ts -> transferResources()
        """
        # TODO: Implement
        pass
    
    def destroy_unit(self, team, unitid):
        """
        Destroys the unit with this id and team and removes from tile
        Implements src/Game/index.ts -> Game.destroyUnit()
        """
        # TODO: Implement
        pass

    def regenerate_trees(self):
        """
        Regenerate trees
        Implements src/Game/index.ts -> Game.regenerateTrees()
        """
        # TODO: Implement
        pass

    def handle_movement_actions(self, actions, match):
        """
        Process given move actions and returns a pruned array of actions that can all be executed with no collisions
        Implements src/Game/index.ts -> Game.handleMovementActions()
        """
        # TODO: Implement
        pass

    
    def is_night(self):
        """
        Is it night.
        Implements src/Game/index.ts -> Game.isNight()
        """
        # TODO: Implement
        pass
    
    
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