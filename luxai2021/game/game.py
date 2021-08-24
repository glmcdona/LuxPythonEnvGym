from .constants import Constants
from .game_map import GameMap
from .game_objects import Player, Unit, City, CityTile, Worker

INPUT_CONSTANTS = Constants.INPUT_CONSTANTS

# TODO: Add all the game logic here!
class Game:
    # Mirrored Game constant enums. All the available agent actions with specifications as to what they do and restrictions.
    class ACTIONS:
        #
        # Formatted as `m unitid direction`. unitid should be valid and should have empty space in that direction. moves
        # unit with id unitid in the direction
        #
        MOVE = 'm',
        #
        # Formatted as `r x y`. (x,y) should be an owned city tile, the city tile is commanded to research for
        # the next X turns
        #/
        RESEARCH = 'r',
        # Formatted as `bw x y`. (x,y) should be an owned city tile, where worker is to be built #/
        BUILD_WORKER = 'bw',
        # Formatted as `bc x y`. (x,y) should be an owned city tile, where the cart is to be built #/
        BUILD_CART = 'bc',
        #
        # Formatted as `bcity unitid`. builds city at unitid's pos, unitid should be
        # friendly owned unit that is a worker
        #/
        BUILD_CITY = 'bcity',
        #
        # Formatted as `t source_unitid destination_unitid resource_type amount`. Both units in transfer should be
        # adjacent. If command valid, it will transfer as much as possible with a max of the amount specified
        #/
        TRANSFER = 't',

        # formatted as `p unitid`. Unit with the given unitid must be owned and pillages the tile they are on #/
        PILLAGE = 'p',

        # formatted as dc <x> <y> #/
        DEBUG_ANNOTATE_CIRCLE = 'dc',
        # formatted as dx <x> <y> #/
        DEBUG_ANNOTATE_X = 'dx',
        # formatted as dl <x1> <y1> <x2> <y2> #/
        DEBUG_ANNOTATE_LINE = 'dl',
        # formatted as dt <x> <y> <message> <fontsize> #/
        DEBUG_ANNOTATE_TEXT = 'dt',
        # formatted as dst <message> #/
        DEBUG_ANNOTATE_SIDETEXT = 'dst'

    class DIRECTIONS:
        NORTH = 'n',
        EAST = 'e',
        SOUTH = 's',
        WEST = 'w',
        CENTER = 'c',


    def __init__(self, config = {"width":20, "height": 20}):
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
        self.map = GameMap(self, config["width"], config["height"])

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
        team_city_count = 0
        for city in self.cities:
            if city.team == team:
                team_city_count += 1
        
        return self.state["teamStates"][team]["units"]["size"] + offset >= team_city_count
    
    def cart_unit_cap_reached(self, team, offset = 0):
        """
        Returns True if unit cap reached
        Implements src/Game/index.ts -> Game.cartUnitCapReached()
        """
        return self.worker_unit_cap_reached(team, offset)
    
    def spawn_worker(self, team, x, y, unitid = None):
        """
        Spawns new worker
        Implements src/Game/index.ts -> Game.spawnWorker()
        """
        cell = self.map.get_cell(x, y)
        unit = Worker(
            x,
            y,
            team,
            self.configs,
            self.global_unitid_count + 1
        )

        if unitid:
            unit.id = unitid
        else:
            self.global_unitid_count += 1
        
        cell.units.set(unit.id, unit)

        self.state.teamStates[team].units.set(unit.id, unit)
        self.stats.teamStats[team].workersBuilt += 1
        return unit

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