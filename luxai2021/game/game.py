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
        return self.state["teamStates"][team]["units"]

    def getUnit(self, team, unitid):
        """
        Get the specific unit.
        Implements src/Game/index.ts -> Game.getUnit()
        """
        return self.state["teamStates"][team]["units"][unitid]
    
    def transferResources(self, team, srcID, destID, resourceType, amount):
        """
        Transfer resouces on a given team between 2 units. This does not check adjacency requirement, but its expected
        that the 2 units are adjacent. This allows for simultaneous movement of 1 unit and transfer of another
        Implements src/Game/index.ts -> transferResources()
        """
        srcunit = self.getUnit(team, srcID)
        destunit = self.getUnit(team, destID)
        # the amount to actually transfer is the minimum of:
        transferAmount = math.min(
            # the amount requested
            amount,
            # and all that we have if that's less than requested
            srcunit.cargo[resourceType],
            # and no more than destination-unit's remaining cargo-space
            destunit.getCargoSpaceLeft()
        )
        srcunit.cargo[resourceType] -= transferAmount
        destunit.cargo[resourceType] += transferAmount
    
    def destroyCity(self, team, cityID):
        """
        Destroys the unit with this id and team and removes from tile
        Implements src/Game/index.ts -> Game.destroyCity()
        """
        city = self.cities.get(cityID)
        self.cities.pop(cityID)
        for cell in city.citycells:
            cell.citytile = None
            cell.road = self.configs.parameters.MIN_ROAD
    
    def destroyUnit(self, team, unitid):
        """
        Destroys the unit with this id and team and removes from tile
        Implements src/Game/index.ts -> Game.destroyUnit()
        """
        unit = self.getUnit(team, unitid);
        self.map.getCellByPos(unit.pos).units.pop(unitid)
        self.state["teamStates"][team]["units"].pop(unitid)

    def regenerateTrees(self):
        """
        Regenerate trees
        Implements src/Game/index.ts -> Game.regenerateTrees()
        /**
        * regenerates trees on map according to the following formula
        * let max_wood_amount be base and the current amount be curr
        *
        * then at the end of each turn after all moves and all resource collection is finished,
        * the wood at a wood tile grows to ceil(min(curr * 1.03, base))
        */
        """
        for cell in self.map.resources_by_type[Constants.RESOURCE_TYPES.WOOD]:
            # add this condition so we let forests near a city start large (but not regrow until below a max)
            if (cell.resource.amount < self.configs["parameters"]["MAX_WOOD_AMOUNT"]):
                cell.resource.amount = math.ceil(
                    math.min(
                        cell.resource.amount * self.configs["parameters"]["WOOD_GROWTH_RATE"],
                        self.configs.parameters.MAX_WOOD_AMOUNT
                    )
                )

    def handleMovementActions(self, actions, match):
        """
        Process given move actions and returns a pruned array of actions that can all be executed with no collisions
        Implements src/Game/index.ts -> Game.handleMovementActions()
        /**
        * Algo:
        *
        * iterate through all moves and store a mapping from cell to the actions that will cause a unit to move there
        *
        * for each cell that has multiple mapped to actions, we remove all actions as that cell is a "bump" cell
        * where no units can get there because they all bumped into each other
        *
        * for all removed actions for that particular cell, find the cell the unit that wants to execute the action is
        * currently at, labeled `origcell`. Revert these removed actions by first getting all the actions mapped from
        * `origcell` and then deleting that mapping, and then recursively reverting the actions mapped from `origcell`
        *
        */
        """
        cellsToActionsToThere = {}
        movingUnits = set()

        for action in actions:
            newcell = action.newcell
            if newcell in cellsToActionsToThere:
                cellsToActionsToThere[newcell] += [action]
            else:
                cellsToActionsToThere[newcell] = [action]
            
            movingUnits.add(action.unitid)

        def revertAction(action):
            # reverts a given action such that cellsToActionsToThere has no collisions due to action and all related actions
            if (match):
                match.log.warn(f"turn {{state.turn}} Unit {{action.unitid}} collided when trying to move {{action.direction}} to ({{action.newcell.pos.x}}, {{action.newcell.pos.y}})")
            
            origcell = self.map.getCellByPos(
                self.getUnit(action.team, action.unitid).pos
            )

            # get the colliding actions caused by a revert of the given action and then delete them from the mapped origcell provided it is not a city tile
            collidingActions = cellsToActionsToThere[origcell] if origcell in cellsToActionsToThere else None
            if (not origcell.isCityTile()):
                cellsToActionsToThere.pop(origcell)

                if (collidingActions is not None):
                    # for each colliding action, revert it.
                    for collidingAction in collidingActions:
                        revertAction(collidingAction)

        actionedCells = list(cellsToActionsToThere.keys())
        for cell in actionedCells:
            currActions = cellsToActionsToThere[cell]
            actionsToRevert = []
            if (currActions != None):
                if (currActions.length > 1):
                    # only revert actions that are going to the same tile that is not a city
                    # if going to the same city tile, we know those actions are from same team units, and is allowed
                    if (not cell.isCityTile()):
                        actionsToRevert += currActions
                elif (currActions.length == 1):
                    # if there is just one move action, check there isn't a unit on there that is not moving and not a city tile
                    action = currActions[0]
                    if (not cell.isCityTile()):
                        if (cell.units.size == 1):
                            unitThereIsStill = True
                            for unit in cell.units:
                                if (movingUnits.has(unit.id)):
                                    unitThereIsStill = False
                            if (unitThereIsStill):
                                actionsToRevert.push(action)
            
            # if there are collisions, revert those actions and remove the mapping
            for action in actionsToRevert:
                revertAction(action)
            for action in actionsToRevert:
                cellsToActionsToThere.delete(action.newcell)
        
        prunedActions = []
        for currActions in cellsToActionsToThere:
            prunedActions.append(currActions)

        return prunedActions
        

    def isNight(self):
        """
        Is it night.
        Implements src/Game/index.ts -> Game.isNight()
        """
        dayLength = self.configs["parameters"]["DAY_LENGTH"]
        cycleLength = dayLength + self.configs["parameters"]["NIGHT_LENGTH"]
        return (self.state["turn"] % cycleLength) >= dayLength
    
    def toStateObject(self):
        """
        Serialize state
        Implements src/Game/index.ts -> Game.toStateObject()
        """
        cities = {}
        for city in self.cities:
            cityCells = []
            for cell in city.citycells:
                cityCells.append({
                    "x": cell.pos.x,
                    "y": cell.pos.y,
                    "cooldown": cell.citytile.cooldown,
                })
            
            cities[city.id] = {
                "id": city.id,
                "fuel": city.fuel,
                "lightupkeep": city.getLightUpkeep(),
                "team": city.team,
                "cityCells": cityCells
            }
        
        state = {
            "turn": self.state.turn,
            "globalCityIDCount": self.globalCityIDCount,
            "globalUnitIDCount": self.globalUnitIDCount,
            "teamStats": {
                Constants.TEAM.A: {
                    "researchPoints": 0,
                    "units": {},
                    "researched": {
                        "wood": True,
                        "coal": False,
                        "uranium": False,
                    },
                },
                Constants.TEAM.B: {
                    "researchPoints": 0,
                    "units": {},
                    "researched": {
                        "wood": True,
                        "coal": False,
                        "uranium": False,
                    },
                },
            },
            map: self.map.toStateObject(),
            "cities" : cities,
        }

        teams = [Constants.TEAM.A, Constants.TEAM.B];
        for team in teams:
            for unit in self.state["teamStates"][team]["units"]:
                state["teamStates"][team]["units"][unit.id] = {
                    "cargo": dict(unit.cargo),
                    "cooldown": unit.cooldown,
                    "x": unit.pos.x,
                    "y": unit.pos.y,
                    "type": unit.type,
                }
            
            state["teamStates"][team]["researchPoints"] = self.state["teamStates"][team]["researchPoints"]
            state["teamStates"][team]["researched"] = dict( self.state["teamStates"][team]["researched"] )

        return state
