import gym
from .constants import Constants, LuxMatchConfigs_Default
from .game_map import GameMap
import traceback

from .unit import Unit, Worker, Cart
from .city import City
import math
import random

INPUT_CONSTANTS = Constants.INPUT_CONSTANTS
DIRECTIONS = Constants.DIRECTIONS

class Game:
    def __init__(self, configs = None, agents = []):
        # Initializations from src/Game/index.ts -> Game()
        self.configs = LuxMatchConfigs_Default
        self.configs.update(configs) # Override default config from specified config
        self.agents = []
        self.reset()
        self.logFile = None

    def reset(self):
        ''' Resets the game for another game. '''
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

        # Generate the map
        self.map = GameMap(self.configs)
        self.map.generateMap(self)

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
    

    def runTurnWithActions(self, actions):
        """
        Runs a single game turn with the specified actions
        Returns:
            True if game is still running
            False if game is over
        """
        if "log" in self.configs and self.configs["log"]:
            self.log('Processing turn ' + self.game.state["turn"])
        
        # Loop over commands and validate and map into internal action representations
        actionsMap = {}

        accumulatedActionStats = self._genInitialAccumulatedActionStats()
        for i, action in enumerate(actions):
            # get the command and the agent that issued it and handle appropriately
            try:
                action = self.validateCommand(
                    actions[i],
                    accumulatedActionStats
                )
                if (action is not None):
                    if action.action in actionsMap:
                        actionsMap[action.action].append(action)
                    else:
                        actionsMap[action.action] = [action]
            except Exception as e:
                self.log("Error processing action")
                self.log(repr(e))
                self.log(traceback.print_exc())

        # give units and city tiles their validated actions to use
        if Constants.ACTIONS.BUILD_CITY in actionsMap:
            for action in actionsMap[Constants.ACTIONS.BUILD_CITY]:
                self.getUnit(action.team, action.unitid).giveAction(action)
        
        if Constants.ACTIONS.BUILD_WORKER in actionsMap:
            for action in actionsMap[Constants.ACTIONS.BUILD_WORKER]:
                citytile = self.map.getCell(action.x, action.y).citytile
                citytile.giveAction(action)
        
        if Constants.ACTIONS.BUILD_CART in actionsMap:
            for action in actionsMap[Constants.ACTIONS.BUILD_CART]:
                citytile = self.map.getCell(action.x, action.y).citytile
                citytile.giveAction(action)
        
        if Constants.ACTIONS.PILLAGE in actionsMap:
            for action in actionsMap[Constants.ACTIONS.PILLAGE]:
                self.getUnit(action.team, action.unitid).giveAction(action)
        
        if Constants.ACTIONS.RESEARCH in actionsMap:
            for action in actionsMap[Constants.ACTIONS.RESEARCH]:
                citytile = self.map.getCell(action.x, action.y).citytile
                citytile.giveAction(action)
        
        if Constants.ACTIONS.TRANSFER in actionsMap:
            for action in actionsMap[Constants.ACTIONS.TRANSFER]:
                self.getUnit(action.team, action.srcID).giveAction(action)

        if Constants.ACTIONS.MOVE in actionsMap:
            prunedMoveActions = self.handleMovementActions(
                actionsMap[Constants.ACTIONS.MOVE]
            )
        else:
            prunedMoveActions = []

        for action in prunedMoveActions:
            # if direction is center, ignore it
            if (action.direction != Constants.DIRECTIONS.CENTER):
                self.getUnit(action.team, action.unitid).giveAction(action)

        # now we go through every actionable entity and execute actions
        for city in self.cities.values():
            for citycell in city.citycells:
                try:
                    citycell.citytile.handleTurn(self)
                except Exception as e:
                    self.log("Critical error handling city turn.")
                    self.log(repr(e))
                    self.log(traceback.print_exc())

        teams = [Constants.TEAM.A, Constants.TEAM.B]
        for team in teams:
            for unit in self.state["teamStates"][team]["units"].values():
                try:
                    unit.handleTurn(self)
                except Exception as e:
                    self.log("Critical error handling unit turn.")
                    self.log(repr(e))
                    self.log(traceback.print_exc())

        # distribute all resources in order of decreasing fuel efficiency
        self.distributeAllResources()

        # now we make all units with cargo drop all resources on the city they are standing on
        for team in teams:
            for unit in self.state["teamStates"][team]["units"].values():
                self.handleResourceDeposit(unit)

        if (self.isNight()):
            self.handleNight()

        # remove resources that are depleted from map
        newResourcesMap = []
        self.map.resources_by_type = {}
        for i in range(len(self.map.resources)):
            cell = self.map.resources[i]
            if (cell.resource.amount > 0):
                newResourcesMap.append(cell)
                if cell.resource.type not in self.map.resources_by_type:
                    self.map.resources_by_type[cell.resource.type] = [cell]
                else:
                    self.map.resources_by_type[cell.resource.type].append(cell)

        self.map.resources = newResourcesMap

        # regenerate forests
        self.regenerateTrees()

        matchOver = self.matchOver()

        self.state["turn"] += 1

        # store state
        # TODO: IMPLEMENT THIS
        #if (self.replay.statefulReplay):
        #    self.replay.writeState(self)

        self.runCooldowns()

        if (matchOver):
            #if (self.replay):
            #    self.replay.writeOut(self.getResults(match))
            return True

        #self.log('Beginning turn %s' % self.state["turn"])
        return False


    def handleNight(self):
        """
        Implements /src/logic.ts -> handleNight()
        /**
        * Handle nightfall and update state accordingly
        */
        """
        for city in list(self.cities.values()):
            # if city does not have enough fuel, destroy it
            # TODO, probably add this event to replay
            if (city.fuel < city.getLightUpkeep()):
                self.destroyCity(city.team, city.id)
            else:
                city.fuel -= city.getLightUpkeep()
        
        for team in [Constants.TEAM.A, Constants.TEAM.B]:
            for unit in list(self.state["teamStates"][team]["units"].values()):
                # TODO: add condition for different light upkeep for units stacked on a city.
                if (not self.map.getCellByPos(unit.pos).isCityTile()):
                    if (not unit.spendFuelToSurvive()):
                        # delete unit
                        self.destroyUnit(unit.team, unit.id)

    def runCooldowns(self):
        """
        Implements /src/Game/index.ts -> runCooldowns()
        """
        for team in [Constants.TEAM.A, Constants.TEAM.B]:
            units = self.getTeamsUnits(team).values()
            for unit in units:
                unit.cooldown -= self.map.getCellByPos(unit.pos).getRoad()
                unit.cooldown = max(unit.cooldown - 1, 0)
    
    def matchOver(self):
        """
        Implements /src/logic.ts -> matchOver()
        /**
        * Determine if match is over or not
        */
        """

        if (self.state["turn"] >= self.configs["parameters"]["MAX_DAYS"] - 1):
            return True
        
        # over if at least one team has no units left or city tiles
        teams = [Constants.TEAM.A, Constants.TEAM.B]
        cityCount = [0, 0]

        for city in self.cities.values():
            cityCount[city.team] += 1

        for team in teams:
            if len(self.getTeamsUnits(team)) + cityCount[team] == 0:
                return True

        return False

    def getWinningTeam(self):
        """
        Implements /src/logic.ts -> getResults()
        """
        
        # count city tiles
        cityTileCount = [0, 0]
        for city in self.cities.values():
            cityTileCount[city.team] += len(city.citycells)
        
        if (cityTileCount[Constants.TEAM.A] > cityTileCount[Constants.TEAM.B]):
            return Constants.TEAM.A
        elif (cityTileCount[Constants.TEAM.A] < cityTileCount[Constants.TEAM.B]):
            return Constants.TEAM.B
        
        # if tied, count by units
        unitCount = [
            len(self.getTeamsUnits(Constants.TEAM.A)),
            len(self.getTeamsUnits(Constants.TEAM.B)),
        ]
        if unitCount[Constants.TEAM.A] > unitCount[Constants.TEAM.B]:
            return Constants.TEAM.A
        elif unitCount[Constants.TEAM.B] > unitCount[Constants.TEAM.A]:
            return Constants.TEAM.B
        
        # if tied still, count by fuel generation
        if (
            self.stats["teamStats"][Constants.TEAM.A]["fuelGenerated"] >
            self.stats["teamStats"][Constants.TEAM.B]["fuelGenerated"]
        ):
            return Constants.TEAM.A
        elif (
            self.stats["teamStats"][Constants.TEAM.A]["fuelGenerated"] <
            self.stats["teamStats"][Constants.TEAM.B]["fuelGenerated"]
        ):
            return Constants.TEAM.B

        # if still undecided, for now, go by random choice
        if ( random.random() > 0.5):
            return Constants.TEAM.A
        return Constants.TEAM.B


    def log(self, text):
        ''' Logs the specified text'''
        if self.logFile == None:
            self.logFile = open("log.txt","w")
        if text != None:
            self.logFile.write(text + "\n")

    def validateCommand(self, cmd, accumulatedActionStats=None):
        """
        Returns an Action object if validated. If invalid, throws MatchWarn
        Implements src/Game/index.ts -> Game.validateCommand()
        """
        if accumulatedActionStats is None:
            accumulatedActionStats = self._genInitialAccumulatedActionStats()

        def check(condition, errormsg, trace = True):
            if (condition):
                if trace:
                    raise Exception(errormsg + "; turn ${this.state.turn}; cmd: ${cmd.command}")
                else:
                    raise Exception(errormsg)
        
        

        
        # TODO: IMPLEMENT THIS
        return cmd

    def workerUnitCapReached(self, team, offset = 0):
        """
        Returns True if unit cap reached
        Implements src/Game/index.ts -> Game.workerUnitCapReached()
        """
        team_city_count = 0
        for city in self.cities.values():
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
        cell = self.map.getCell(x, y)

        # now update the cities field accordingly
        adjCells = self.map.getAdjacentCells(cell)

        cityIdsFound = set()

        adjSameTeamCityTiles = []
        for cell2 in adjCells:
            if cell2.isCityTile() and cell2.citytile.team == team:
                adjSameTeamCityTiles.append(cell2)
                cityIdsFound.add(cell2.citytile.cityid)

        # if no adjacent city cells of same team, generate new city
        if len(adjSameTeamCityTiles) == 0:
            city = City(team, self.configs, self.globalCityIDCount + 1)

            if cityid != None:
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
            cell.citytile.adjacentCityTiles = len(adjSameTeamCityTiles)
            for adjCell in adjSameTeamCityTiles:
                adjCell.citytile.adjacentCityTiles += 1
            city.addCityTile(cell)

            # update all merged cities' cells with merged cityid, move to merged city and delete old city
            for id in cityIdsFound:
                if id != cityid:
                    oldcity = self.cities[id]
                    for cell3 in oldcity.citycells:
                        cell3.citytile.cityid = cityid
                        city.addCityTile(cell3)
                
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

        for curType in miningOrder:
            self.handleResourceTypeRelease(curType)


    def handleResourceTypeRelease(self, resourceType):
        """
        * For each unit, check current and orthoganally adjancent cells for that resource
        * type. If found, request as much as we can carry from these cells. In the case of un-even 
        * amounts, the unit will request an equal amount from all tiles to fill their cargo, then
        * discard the rest. (for example on 3 wood tiles with 60 wood it would request 17 to each
        * wood tile and discard/waste the extra 1 wood mined).
        * 
        * If the unit is on a city tile, only one request will be made (even if there are 
        * multiple workers on the tile )and the resources will be deposited into the city as fuel.
        * 
        * Once all units have requested resources, distrubte the resources, reducing requests
        * requests if it would exceed the current value. In this case the remaining
        * will be distributed evenly, with the leftovers discarded.
        * 
        * @param resourceType - the type of the resource
        * Description copy pasted from src/Game/index.ts -> Game.handleResourceTypeRelease()
        """
        # build up the resource requests
        requests = self.createResourceRequests(resourceType)

        # resolve resource requests
        self.resolveResourceRequests(resourceType, requests)


    class ResourceRequest:
        def __init__(self, fromPos, amount, worker, city):
            self.fromPos = fromPos
            self.amount = amount
            self.worker = worker
            self.city = city

        def __eq__(self, other) -> bool:
            return ( 
                self.fromPos == other.fromPos
                and (self.worker.id if self.worker else None) == (other.worker.id if other.worker else None)
                and self.amount == other.amount
                and (self.city.id if self.city else None) == (other.city.id if other.city else None)
                )
    
    def createResourceRequests(self, resourceType):
        type_map = {
                Constants.RESOURCE_TYPES.WOOD : "WOOD",
                Constants.RESOURCE_TYPES.COAL : "COAL",
                Constants.RESOURCE_TYPES.URANIUM : "URANIUM",
        }
        miningRate = rate = self.configs["parameters"]["WORKER_COLLECTION_RATE"][type_map[resourceType]]
        reqs = {}
        for team in [Constants.TEAM.A, Constants.TEAM.B]:
            if self.state["teamStates"][team]["researched"][resourceType]:
                for unit in self.state["teamStates"][team]["units"].values():
                    if unit.type == Constants.UNIT_TYPES.WORKER:
                        unitCell = self.map.getCellByPos(unit.pos)
                        cells = [unitCell] + self.map.getAdjacentCells(unitCell)
                        minable = [c for c in cells if c.hasResource() and c.resource.type == resourceType]
                        if len(minable) > 0:
                            mineAmount = min(math.ceil(unit.getCargoSpaceLeft() / len(minable)), miningRate)
                        for cell in minable:
                            if cell.pos not in reqs:
                                reqs[cell.pos] = []
                            req = Game.ResourceRequest(
                                unit.pos, 
                                mineAmount, 
                                None if unitCell.isCityTile() else unit, 
                                self.cities[unitCell.citytile.cityid] if unitCell.isCityTile() else None, 
                                )
                            hasReq = req in reqs[cell.pos]
                            if not hasReq:
                                reqs[cell.pos].append(req)
        return reqs

    def resolveResourceRequests(self, resourceType, requests):
        type_map = {
                Constants.RESOURCE_TYPES.WOOD : "WOOD",
                Constants.RESOURCE_TYPES.COAL : "COAL",
                Constants.RESOURCE_TYPES.URANIUM : "URANIUM",
        }
        conversionRate = self.configs["parameters"]["RESOURCE_TO_FUEL_RATE"][type_map[resourceType]]
        for position, reqs in requests.items():
            amountLeft = self.map.getCellByPos(position).resource.amount
            amountsReqs = reqs # dont make tuples like typescript reference implementation
            while len(amountsReqs) > 0 and sum([req.amount for req in amountsReqs]) > 0 and amountLeft > 0:
                toFill = min(min([req.amount for req in amountsReqs]), math.floor(amountLeft/len(amountsReqs)))
                for r in amountsReqs:
                    if r.city is not None:
                        self.stats["teamStats"][r.city.team]["resourcesCollected"][resourceType] += toFill
                        r.city.fuel += toFill * conversionRate
                    else:
                        toGive = min(r.worker.getCargoSpaceLeft(), toFill)
                        self.stats["teamStats"][r.worker.team]["resourcesCollected"][resourceType] += toGive
                        r.worker.cargo[resourceType] += toGive
                    r.amount -= toFill
                amountLeft -= toFill * len(amountsReqs)
                if amountLeft < len(amountsReqs):
                    amountLeft = 0
                amountsReqs = list(filter(lambda r: r.amount>0, amountsReqs))
            cell = self.map.getCellByPos(position)
            cell.resource.amount = amountLeft
        
    
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
            cell.road = self.configs["parameters"]["MIN_ROAD"]
    
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
        if Constants.RESOURCE_TYPES.WOOD in self.map.resources_by_type:
            for cell in self.map.resources_by_type[Constants.RESOURCE_TYPES.WOOD]:
                # add this condition so we let forests near a city start large (but not regrow until below a max)
                if (cell.resource.amount < self.configs["parameters"]["MAX_WOOD_AMOUNT"]):
                    cell.resource.amount = math.ceil(
                        min(
                            cell.resource.amount * self.configs["parameters"]["WOOD_GROWTH_RATE"],
                            self.configs["parameters"]["MAX_WOOD_AMOUNT"]
                        )
                    )

    def handleMovementActions(self, actions):
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
            newcell = self.map.getCellByPos(
                self.getUnit(action.team, action.unitid).pos.translate(action.direction, 1)
            )
            if newcell != None:
                #newcell = action.newcell
                if newcell in cellsToActionsToThere:
                    cellsToActionsToThere[newcell] += [action]
                else:
                    cellsToActionsToThere[newcell] = [action]
                
                movingUnits.add(action.unitid)

        def revertAction(action):
            # reverts a given action such that cellsToActionsToThere has no collisions due to action and all related actions
            self.log(f"turn {{self.state['turn']}} Unit {{action.unitid}} collided when trying to move {{action.direction}} to ({{action.newcell.pos.x}}, {{action.newcell.pos.y}})")
            
            origcell = self.map.getCellByPos(
                self.getUnit(action.team, action.unitid).pos
            )

            # get the colliding actions caused by a revert of the given action and then delete them from the mapped origcell provided it is not a city tile
            collidingActions = cellsToActionsToThere[origcell] if origcell in cellsToActionsToThere else None
            if (not origcell.isCityTile()):
                if (collidingActions is not None):
                    cellsToActionsToThere.pop(origcell)

                    # for each colliding action, revert it.
                    for collidingAction in collidingActions:
                        revertAction(collidingAction)

        actionedCells = list(cellsToActionsToThere.keys())
        for cell in actionedCells:
            if cell in cellsToActionsToThere:
                currActions = cellsToActionsToThere[cell]
                actionsToRevert = []
                if (currActions != None):
                    if (len(currActions) > 1):
                        # only revert actions that are going to the same tile that is not a city
                        # if going to the same city tile, we know those actions are from same team units, and is allowed
                        if (not cell.isCityTile()):
                            actionsToRevert += currActions
                    elif (len(currActions) == 1):
                        # if there is just one move action, check there isn't a unit on there that is not moving and not a city tile
                        action = currActions[0]
                        if (not cell.isCityTile()):
                            if (len(cell.units) == 1):
                                unitThereIsStill = True
                                for unit in cell.units.values():
                                    if (unit.id in movingUnits):
                                        unitThereIsStill = False
                                if (unitThereIsStill):
                                    actionsToRevert.append(action)
            
            # if there are collisions, revert those actions and remove the mapping
            for action in actionsToRevert:
                revertAction(action)
            for action in actionsToRevert:
                newcell = self.map.getCellByPos(
                    self.getUnit(action.team, action.unitid).pos.translate(action.direction, 1)
                )
                if newcell in cellsToActionsToThere:
                    cellsToActionsToThere.pop(newcell)
        
        prunedActions = []
        for currActions in cellsToActionsToThere.values():
            prunedActions += currActions

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
        for city in self.cities.values():
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
            "turn": self.state["turn"],
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
            for unit in self.state["teamStates"][team]["units"].values():
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
