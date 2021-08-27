'''Implements /src/logic.ts '''

import math
import random
from .constants import Constants
from .gen import generateGame
from .agent import Agent

class Match():
    '''Roughly implements /src/logic.ts -> LuxDesignLogic()'''
    def __init(self, configs, agent1 : Agent, agent2 : Agent):
        # Merge config with default template
        self.configs = dict(Constants.LuxMatchConfigs_Default).update(configs)
        self.game = None
        self.agents = [agent1, agent2]

        self.initialize()

    # Initialization step of each match
    def initialize(self):
        # Generate the game and map
        self.game = generateGame(self.configs)

        # Initialize the agents
        for agent in self.agents:
            agent.initialize(self.game, self.configs)


    def log(self, text):
        ''' Logs the specified text'''
        print(text) # TODO: Log to file as well?


    # Update step of each match, called whenever the match moves forward by a single unit in time (1 timeStep)
    def run_turn(self):
        if "log" in self.configs and self.configs["log"]:
            self.log('Processing turn ' + self.game.state.turn)
        
        # loop over commands and validate and map into internal action representations
        actionsMap: Map<Constants.ACTIONS, Array<Action>> = new Map()
        Object.values(Constants.ACTIONS).forEach((val) => {
        actionsMap.set(val, [])
        })

        accumulatedActionStats = game._genInitialAccumulatedActionStats()
        for (let i = 0 i < commands.length i++) {
        # get the command and the agent that issued it and handle appropriately
        try {
            action = game.validateCommand(
            commands[i],
            accumulatedActionStats
            )
            if (action not = null) {
            # TODO: this might be slow, depends on its optimized and compiled
            newactionArray = [...actionsMap.get(action.action), action]
            actionsMap.set(action.action, newactionArray)
            }
        } catch (err) {
            match.log.warn(`${err.message}`)
        }
        }

        # give units and city tiles their validated actions to use
        actionsMap
        .get(Constants.ACTIONS.BUILD_CITY)
        .forEach((action: SpawnCityAction) => {
            game.getUnit(action.team, action.unitid).giveAction(action)
        })
        actionsMap
        .get(Constants.ACTIONS.BUILD_WORKER)
        .forEach((action: SpawnWorkerAction) => {
            citytile = game.map.getCell(action.x, action.y).citytile
            citytile.giveAction(action)
        })
        actionsMap
        .get(Constants.ACTIONS.BUILD_CART)
        .forEach((action: SpawnCartAction) => {
            citytile = game.map.getCell(action.x, action.y).citytile
            citytile.giveAction(action)
        })
        actionsMap.get(Constants.ACTIONS.PILLAGE).forEach((action: PillageAction) => {
        game.getUnit(action.team, action.unitid).giveAction(action)
        })
        actionsMap.get(Constants.ACTIONS.RESEARCH).forEach((action: ResearchAction) => {
        citytile = game.map.getCell(action.x, action.y).citytile
        citytile.giveAction(action)
        })
        actionsMap.get(Constants.ACTIONS.TRANSFER).forEach((action: TransferAction) => {
        game.getUnit(action.team, action.srcID).giveAction(action)
        })

        prunedMoveActions = game.handleMovementActions(
        actionsMap.get(Constants.ACTIONS.MOVE) as Array<MoveAction>,
        match
        )

        prunedMoveActions.forEach((action) => {
        # if direction is center, ignore it
        if (action.direction not == Constants.DIRECTIONS.CENTER) {
            game.getUnit(action.team, action.unitid).giveAction(action)
        }
        })

        # now we go through every actionable entity and execute actions
        game.cities.forEach((city) => {
        city.citycells.forEach((cellWithCityTile) => {
            try {
            cellWithCityTile.citytile.handleTurn(game)
            } catch (err) {
            match.throw(cellWithCityTile.citytile.team, err)
            }
        })
        })
        teams = [Unit.TEAM.A, Unit.TEAM.B]
        for (team of teams) {
        game.state["teamStates"][team]["units"].forEach((unit) => {
            try {
            unit.handleTurn(game)
            } catch (err) {
            match.log.warn(`${err.message}`)
            }
        })
        }

        # distribute all resources in order of decreasing fuel efficiency
        game.distributeAllResources()

        # now we make all units with cargo drop all resources on the city they are standing on
        for (team of teams) {
        game.state["teamStates"][team]["units"].forEach((unit) => {
            game.handleResourceDeposit(unit)
        })
        }

        if (game.isNight()) {
        self.handleNight(state)
        }

        # remove resources that are depleted from map
        newResourcesMap: Array<Cell> = []
        for (let i = 0 i < game.map.resources.length i++) {
        cell = game.map.resources[i]
        if (cell.resource.amount > 0) {
            newResourcesMap.push(cell)
        }
        }
        game.map.resources = newResourcesMap

        # regenerate forests
        game.regenerateTrees()

        if (state.configs["debug) {
        await self.debugViewer(game)
        }
        matchOver = self.matchOver(match)

        game.state.turn++

        # store state
        if (game.replay.statefulReplay) {
        game.replay.writeState(game)
        }

        game.runCooldowns()

        ''' Agent Update Section '''
        await self.sendAllAgentsGameInformation(match)
        # tell all agents updates are done
        donemsgs: Promise<boolean>[] = []
        match.agents.forEach((agent) => {
        if (not agent.isTerminated()) {
            donemsgs.push(match.send('D_DONE', agent))
        }
        })
        
        await Promise.all(donemsgs)

        if (matchOver) {
        if (game.replay) {
            game.replay.writeOut(self.getResults(match))
        }
        return 'finished' as Match.Status.FINISHED
        }

        if (game.configs.runProfiler) {
        etime = new Date().valueOf()
        state.profile.updateStage.push(etime - stime)
        }

        match.log.detail('Beginning turn ' + game.state.turn)

  static async debugViewer(game: Game): Promise<void> {
    console.clear()
    console.log(game.map.getMapString())
    console.log(`Turn: ${game.state.turn}`)
    teams = [Unit.TEAM.A, Unit.TEAM.B]
    for (team of teams) {
      teamstate = game.state["teamStates"][team]
      msg = `RP: ${teamstate["researchPoints"]} | Units: ${teamstate.units.size}`
      # teamstate.units.forEach((unit) => {
      #   msg += `| ${unit.id} (${unit.pos.x}, ${
      #     unit.pos.y
      #   }) cargo space: ${unit.getCargoSpaceLeft()}`
      # })
      if (team == Unit.TEAM.A) {
        console.log(msg.cyan)
      } else {
        console.log(msg.red)
      }
    }
    game.cities.forEach((city) => {
      let iden = `City ${city.id}`.red
      if (city.team == 0) {
        iden = `City ${city.id}`.cyan
      }
      console.log(
        `${iden} light: ${city.fuel} - size: ${city.citycells.length}`
      )
    })
    await sleep(game.configs.debugDelay)
  }

  '''
   * Determine if match is over or not
   * @param state
   '''
  static matchOver(match: Match): boolean {
    state: Readonly<LuxMatchState> = match.state
    game = state.game

    if (game.state.turn == state.configs["parameters.MAX_DAYS - 1) {
      return true
    }
    # over if at least one team has no units left or city tiles
    teams = [Unit.TEAM.A, Unit.TEAM.B]
    cityCount = [0, 0]

    game.cities.forEach((city) => {
      cityCount[city.team] += 1
    })

    for (team of teams) {
      if (game.getTeamsUnits(team).size + cityCount[team] == 0) {
        return true
      }
    }
  }

  '''
   * Handle nightfall and update state accordingly
   * @param state
   '''
  static handleNight(state: LuxMatchState): void {
    game = state.game
    game.cities.forEach((city) => {
      # if city does not have enough fuel, destroy it
      # TODO, probably add this event to replay
      if (city.fuel < city.getLightUpkeep()) {
        game.destroyCity(city.id)
      } else {
        city.fuel -= city.getLightUpkeep()
      }
    })
    [Unit.TEAM.A, Unit.TEAM.B].forEach((team) => {
      game.state["teamStates"][team]["units"].forEach((unit) => {
        # TODO: add condition for different light upkeep for units stacked on a city.
        if (not game.map.getCellByPos(unit.pos).isCityTile()) {
          if (not unit.spendFuelToSurvive()) {
            # delete unit
            game.destroyUnit(unit.team, unit.id)
          }
        }
      })
    })
  }
  static getResults(match: Match): any {
    # calculate results
    state: LuxMatchState = match.state
    game = state.game
    let winningTeam = Unit.TEAM.A
    let losingTeam = Unit.TEAM.B
    figureresults: {
      # count city tiles
      cityTileCount = [0, 0]
      game.cities.forEach((city) => {
        cityTileCount[city.team] += city.citycells.length
      })
      if (cityTileCount[Unit.TEAM.A] > cityTileCount[Unit.TEAM.B]) {
        break figureresults
      } else if (cityTileCount[Unit.TEAM.A] < cityTileCount[Unit.TEAM.B]) {
        winningTeam = Unit.TEAM.B
        losingTeam = Unit.TEAM.A
        break figureresults
      }

      # if tied, count by units
      unitCount = [
        game.getTeamsUnits(Unit.TEAM.A),
        game.getTeamsUnits(Unit.TEAM.B),
      ]
      if (unitCount[Unit.TEAM.A].size > unitCount[Unit.TEAM.B].size) {
        break figureresults
      } else if (unitCount[Unit.TEAM.A].size < unitCount[Unit.TEAM.B].size) {
        winningTeam = Unit.TEAM.B
        losingTeam = Unit.TEAM.A
        break figureresults
      }
      # if tied still, return a tie
      results = {
        ranks: [
          { rank: 1, agentID: winningTeam },
          { rank: 1, agentID: losingTeam },
        ],
        replayFile: null,
      }
      if (game.configs.storeReplay) {
        results.replayFile = game.replay.replayFilePath
      }
      return results

      # # if tied still, count by fuel generation
      # if (
      #   game.stats.teamStats[Unit.TEAM.A].fuelGenerated >
      #   game.stats.teamStats[Unit.TEAM.B].fuelGenerated
      # ) {
      #   break figureresults
      # } else if (
      #   game.stats.teamStats[Unit.TEAM.A].fuelGenerated <
      #   game.stats.teamStats[Unit.TEAM.B].fuelGenerated
      # ) {
      #   winningTeam = Unit.TEAM.B
      #   losingTeam = Unit.TEAM.A
      #   break figureresults
      # }

      # # if still undecided, for now, go by random choice
      # if (state.rng() > 0.5) {
      #   winningTeam = Unit.TEAM.B
      #   losingTeam = Unit.TEAM.A
      # }
    }

    results = {
      ranks: [
        { rank: 1, agentID: winningTeam },
        { rank: 2, agentID: losingTeam },
      ],
      replayFile: null,
    }
    if (game.configs.storeReplay) {
      results.replayFile = game.replay.replayFilePath
    }
    return results
  }

  '''
   * Reset the match to a starting state and continue from there
   * @param serializedState
   *
   * DOES NOT change constants at all
   '''
  static reset(
    match: Match,
    serializedState: SerializedState | KaggleObservation
  ): void {
    '''
     * For this to work correctly, spawn all entities in first, then update any stats / global related things as
     * some spawning functions updates the stats or globals e.g. global ids
     '''
    state: LuxMatchState = match.state
    game = state.game
    function isKaggleObs(
      obs: SerializedState | KaggleObservation
    ): obs is KaggleObservation {
      return (obs as KaggleObservation).updates not == undefined
    }
    if (isKaggleObs(serializedState)) {
      # handle reduced states (e.g. kaggle outputs)
      serializedState = parseKaggleObs(serializedState)
    }
    # update map first
    height = serializedState.map.length
    width = serializedState.map[0].length

    configs = {
      ...game.configs,
    }
    configs.width = width
    configs.height = height
    game.map = new GameMap(configs)

    for (let y = 0 y < height y++) {
      for (let x = 0 x < width x++) {
        cellinfo = serializedState.map[y][x]
        if (cellinfo.resource) {
          game.map.addResource(
            x,
            y,
            cellinfo.resource.type as Resource.Types,
            cellinfo.resource.amount
          )
        }
        cell = game.map.getCell(x, y)
        cell.road = cellinfo.road
      }
    }

    # spawn in cities
    game.cities = new Map()
    for (cityid of Object.keys(serializedState.cities)) {
      cityinfo = serializedState.cities[cityid]
      cityinfo.cityCells.forEach((ct) => {
        tile = game.spawnCityTile(cityinfo.team, ct.x, ct.y, cityinfo.id)
        tile.cooldown = ct.cooldown
      })
      city = game.cities.get(cityinfo.id)
      city.fuel = cityinfo.fuel
    }

    teams = [Unit.TEAM.A, Unit.TEAM.B]
    for (team of teams) {
      game.state["teamStates"][team]["researchPoints"] =
        serializedState.teamStates[team]["researchPoints"]
      game.state["teamStates"][team]["researched"] = deepCopy(
        serializedState.teamStates[team]["researched"]
      )
      game.state["teamStates"][team]["units"].clear()
      for (unitid of Object.keys(
        serializedState.teamStates[team]["units"]
      )) {
        unitinfo = serializedState.teamStates[team]["units"][unitid]
        let unit: Unit
        if (unitinfo.type == Constants.UNIT_TYPES.WORKER) {
          unit = game.spawnWorker(team, unitinfo.x, unitinfo.y, unitid)
        } else {
          unit = game.spawnCart(team, unitinfo.x, unitinfo.y, unitid)
        }
        unit.cargo = deepCopy(unitinfo.cargo)
        unit.cooldown = deepCopy(unitinfo.cooldown)
      }
    }

    # update globals
    game.state.turn = serializedState.turn
    game.globalCityIDCount = serializedState.globalCityIDCount
    game.globalUnitIDCount = serializedState.globalUnitIDCount
    # game.stats = deepCopy(serializedState.stats)

    # without this, causes some bugs
    game.map.sortResourcesDeterministically()
  }