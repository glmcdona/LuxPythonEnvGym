from .constants import Constants, LuxMatchConfigs_Default
from .game_map import GameMap

from .unit import Unit, Worker, Cart
from .city import City
import math

INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
DIRECTIONS = Constants.DIRECTIONS

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


    def __init__(self, configs = None):
        # Initializations from src/Game/index.ts -> Game()
        self.configs = LuxMatchConfigs_Default
        self.configs.update(configs) # Override default config from specified config

        self.globalCityIDCount = 0
        self.globalUnitIDCount = 0
        self.cities = {} # string -> City
        self.stats = {
            "teamStats": {
                Constants.TEAM.A: {
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
                Constants.TEAM.B: {
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
                Constants.TEAM.A : {
                    "researchPoints": 0,
                    "units" : {},
                    "researched" : {
                        "wood" : True,
                        "coal" : False,
                        "uranium" : False,
                    }
                },
                Constants.TEAM.B : {
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
        self.map = GameMap(self.configs)

    def _genInitialAccumulatedActionStats(self):
        """
        Initial stats
        Implements src/Game/index.ts -> Game._genInitialAccumulatedActionStats()
        """
        return {
                Constants.TEAM.A: {
                    "workersBuilt": 0,
                    "cartsBuilt": 0,
                    "actionsPlaced": set(),
                },
                Constants.TEAM.B: {
                    "workersBuilt": 0,
                    "cartsBuilt": 0,
                    "actionsPlaced": set(),
                },
            }
    
    def validateCommand(self, cmd, accumulatedActionStats=None):
        """
        Returns an Action object if validated. If invalid, throws MatchWarn
        Implements src/Game/index.ts -> Game.validateCommand()
        """
        if accumulatedActionStats is None:
            accumulatedActionStats = self._genInitialAccumulatedActionStats()
        
        # TODO: Implement
        pass

    def workerUnitCapReached(self, team, offset = 0):
        """
        Returns True if unit cap reached
        Implements src/Game/index.ts -> Game.workerUnitCapReached()
        """
        team_city_count = 0
        for city in self.cities:
            if city.team == team:
                team_city_count += 1
        
        return len(self.state["teamStates"][team]["units"]) + offset >= team_city_count
    
    def cartUnitCapReached(self, team, offset = 0):
        """
        Returns True if unit cap reached
        Implements src/Game/index.ts -> Game.cartUnitCapReached()
        """
        return self.worker_unit_cap_reached(team, offset)
    
    def spawnWorker(self, team, x, y, unitid = None):
        """
        Spawns new worker
        Implements src/Game/index.ts -> Game.spawnWorker()
        """
        cell = self.map.getCell(x, y)
        unit = Worker(
            x,
            y,
            team,
            self.configs,
            self.globalUnitIDCount + 1
        )

        if unitid:
            unit.id = unitid
        else:
            self.globalUnitIDCount += 1
        
        cell.units[unit.id] = unit

        self.state["teamStates"][team]["units"][unit.id] = unit
        self.stats["teamStats"][team]["workersBuilt"] += 1
        return unit

    def spawnCart(self, team, x, y, unitid = None):
        """
        Spawns new cart
        Implements src/Game/index.ts -> Game.spawnCart()
        """
        cell = self.map.getCell(x, y)
        unit = Cart(x, y, team, self.configs, self.globalUnitIDCount + 1)
        if unitid:
            unit.id = unitid
        else:
            self.globalUnitIDCount += 1
        
        cell.units[unit.id] = unit
        self.state["teamStates"][team]["units"][unit.id] = unit
        self.stats["teamStats"][team]["cartsBuilt"] += 1
        return unit

    def spawnCityTile(self, team, x, y, cityid = None):
        """
        Spawns new city tile
        Implements src/Game/index.ts -> Game.spawnCityTile()
        """
        cell = self.map.getCell(x, y);

        # now update the cities field accordingly
        adjCells = self.map.getAdjacentCells(cell);

        cityIdsFound = set()

        adjSameTeamCityTiles = []
        for cell in adjCells:
            if cell.isCityTile() and cell.citytile.team == team:
                adjSameTeamCityTiles.append(cell)
                cityIdsFound.add(cityid)

        # if no adjacent city cells of same team, generate new city
        if len(adjSameTeamCityTiles) == 0:
            city = City(team, self.configs, self.globalCityIDCount + 1)

            if cityid:
                city.id = cityid
            else:
                self.globalCityIDCount += 1
            
            cell.setCityTile(team, city.id)
            city.addCityTile(cell)
            self.cities[city.id] = city
            return cell.citytile
        
        else:
            # otherwise add tile to city
            cityid = adjSameTeamCityTiles[0].citytile.cityid
            city = self.cities[cityid]
            cell.setCityTile(team, cityid)

            # update adjacency counts for bonuses
            cell.citytile.adjacentCityTiles = adjSameTeamCityTiles.length
            for cell in adjSameTeamCityTiles:
                cell.citytile.adjacentCityTiles += 1
            city.addCityTile(cell)

            # update all merged cities' cells with merged cityid, move to merged city and delete old city
            for cityid in cityIdsFound:
                if id != cityid:
                    oldcity = self.cities[id]
                    for cell in oldcity.citycells:
                        cell.citytile.cityid = cityid
                        city.addCityTile(cell)
                
                city.fuel += oldcity.fuel
                self.cities.pop(oldcity.id)
            
            return cell.citytile

    def moveUnit(self, team, unitid, direction):
        """
        Moves a unit
        Implements src/Game/index.ts -> Game.moveUnit()
        """
        unit = self.getUnit(team, unitid)

        # remove unit from old cell and move to new one and update unit pos
        self.map.getCellByPos(unit.pos).units.pop(unit.id)
        unit.pos = unit.pos.translate(direction, 1)
        self.map.getCellByPos(unit.pos).units[unit.id] = unit

    def distributeAllResources(self):
        """
        Distributes resources
        Implements src/Game/index.ts -> Game.distributeAllResources()
        """
        miningOrder = [
            Constants.RESOURCE_TYPES.URANIUM,
            Constants.RESOURCE_TYPES.COAL,
            Constants.RESOURCE_TYPES.WOOD,
        ]

        # Note: I optimized this loop from the base game to potentially improve perf. Seemed
        # like this may have been one of the more-costly part of the update loop.
        for curType in miningOrder:
            for cell in self.map.resources_by_type[curType]:
                self.handleResourceRelease(cell)

    def handleResourceRelease(self, originalCell):
        """
        For cells with resources, this will release the resource to all adjacent workers (including any unit on top)
        Implements src/Game/index.ts -> Game.handleResourceRelease()

        * For cells with resources, this will release the resource to all adjacent workers (including any unit on top) in a
        * even manner and taking in account for the worker's team's research level. This is effectively a worker mining.
        *
        * Workers adjacent will only receive resources if they can mine it. They will
        * never receive more than they carry
        *
        * This function is called on cells in the order of uranium, coal, then wood resource deposits
        *
        *
        * @param cell - a cell with a resource
        """
        if (originalCell.hasResource()):
            type = originalCell.resource.type;
            cells = [originalCell, self.map.getAdjacentCells(originalCell)]
            workersToReceiveResources = []
            for cell in cells:
                if (cell.isCityTile() and cell.units.size > 0 and self.state["teamStates"][cell.citytile.team]["researched"][type]):
                    workersToReceiveResources.append(cell.citytile)
                else:
                    for unit in cell.units:
                        # note, this loop only appends one unit to the array since we can only have one unit per city tile
                        if unit.type == Unit.Type.WORKER and self.state["teamStates"][unit.team]["researched"][type]:
                            workersToReceiveResources.append(unit)

            def isWorker(pet):
                return isinstance(pet, Worker)
            
            rate = self.configs["parameters"]["WORKER_COLLECTION_RATE"][type.upper()]
            conversionRate = self.configs["parameters"]["RESOURCE_TO_FUEL_RATE"][type.upper()]

            # find out how many resources to distribute and release
            amountToDistribute = rate * len(workersToReceiveResources)
            amountDistributed = 0
            # distribute only as much as the cell contains
            amountToDistribute = min(
                amountToDistribute,
                originalCell.resource.amount
            )

            # distribute resources as evenly as possible

            # sort from least space to most so those with more capacity will have the correct distribution of resources before we reach cargo capacity
            workersToReceiveResources.sort(key=lambda s: s.getCargoSpaceLeft(), reverse=True) # TODO: Validate Cities get prioritized correctly here. Cities get last priority with this.
            
            for i, entity in enumerate(workersToReceiveResources):
                spaceLeft = entity.getCargoSpaceLeft()
                maxReceivable = amountToDistribute / (len(workersToReceiveResources) - i)
                
                distributeAmount = min(spaceLeft, maxReceivable, rate)
                # we give workers a floored amount for sake of integers and effectiely waste the remainder
                if (isWorker(entity)):
                    entity.cargo[type] += math.floor(distributeAmount)
                else:
                    city = self.cities.get(entity.cityid)
                    city.fuel += conversionRate * math.floor(distributeAmount)

                amountDistributed += distributeAmount

                # update stats
                self.stats["teamStats"][entity.team]["resourcesCollected"][type] += math.floor(distributeAmount)

                # subtract how much was given.
                amountToDistribute -= distributeAmount

            originalCell.resource.amount -= amountDistributed

        
    
    def handleResourceDeposit(self, unit):
        """
        Auto deposit resources of unit to tile it is on
        Implements src/Game/index.ts -> Game.handleResourceDeposit()
        """
        cell = self.map.getCellByPos(unit.pos)
        if (cell.isCityTile() and cell.citytile.team == unit.team):
            city = self.cities.get(cell.citytile.cityid)
            fuelGained = 0
            fuelGained += unit.cargo["wood"] * self.configs["parameters"]["RESOURCE_TO_FUEL_RATE"]["WOOD"]
            fuelGained += unit.cargo["coal"] * self.configs["parameters"]["RESOURCE_TO_FUEL_RATE"]["COAL"]
            fuelGained += unit.cargo["uranium"] * self.configs["parameters"]["RESOURCE_TO_FUEL_RATE"]["URANIUM"]
            city.fuel += fuelGained

            self.stats["teamStats"][unit.team]["fuelGenerated"] += fuelGained

            unit.cargo = {
                "wood": 0,
                "uranium": 0,
                "coal": 0,
            }

    def getTeamsUnits(self, team):
        """
        Get list of units.
        Implements src/Game/index.ts -> Game.getTeamsUnits()
        """
        # TODO: Implement
        pass

    def getUnit(self, team, unitid):
        """
        Get the specific unit.
        Implements src/Game/index.ts -> Game.getUnit()
        """
        # TODO: Implement
        pass
    
    def transferResources(self, team, src_unitid, dest_unitid, resource_type, amount):
        """
        Transfer resouces on a given team between 2 units. This does not check adjacency requirement, but its expected
        that the 2 units are adjacent. This allows for simultaneous movement of 1 unit and transfer of another
        Implements src/Game/index.ts -> transferResources()
        """
        # TODO: Implement
        pass
    
    def destroyUnit(self, team, unitid):
        """
        Destroys the unit with this id and team and removes from tile
        Implements src/Game/index.ts -> Game.destroyUnit()
        """
        # TODO: Implement
        pass

    def regenerateTrees(self):
        """
        Regenerate trees
        Implements src/Game/index.ts -> Game.regenerateTrees()
        """
        # TODO: Implement
        pass

    def handleMovementActions(self, actions, match):
        """
        Process given move actions and returns a pruned array of actions that can all be executed with no collisions
        Implements src/Game/index.ts -> Game.handleMovementActions()
        """
        # TODO: Implement
        pass

    
    def isNight(self):
        """
        Is it night.
        Implements src/Game/index.ts -> Game.isNight()
        """
        # TODO: Implement
        pass
    
    
    '''
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
    '''