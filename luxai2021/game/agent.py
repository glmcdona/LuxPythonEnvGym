''' Implements the base class for a training Agent '''

import time
from typing import Match
from .game import Game
import random
import json
import gym
from gym import spaces
import numpy as np
from functools import partial # pip install functools
from .actions import *
from .constants import Constants


class AgentOpponent():
    def __init__(self, game) -> None:
        self.game = game
    
    def decide_action(self, unitid, cityid, team, newTurn):
        """ Decide on the action for a specific unit """
        pass


class MatchController():
    def __init__(self, game, agents = [None, None]) -> None:
        self.actionBuffer = []
        self.game = game
        self.agents = agents

    def reset(self):
        # Reset the game
        self.game.reset()

    def take_action(self, action):
        """ Adds the specified action to the action buffer """
        self.actionBuffer.append(action)
    
    def run_to_next_observation(self):
        """ 
            Generator function that gets the observation at the next Unit/City
            to be controlled.
            Returns: tuple describing the unit who's control decision is for (unitid, city, team, is new turn)
        """
        game_over = False
        while not game_over:
            for turn in range(360):
                # Process this turn
                
                # Handle each team making decisions for their units and cities for this turn
                actionsTimeTaken = [0.0, 0.0] # Tracks the amount of time used per agent per turn
                for team in [Constants.TEAM.A, Constants.TEAM.B]:
                    newTurn = True
                    is_opponent = issubclass(self.agents[team], AgentOpponent) or isinstance(self.agents[team], AgentOpponent)
                    units = self.state["teamStates"][team]["units"]
                    start_time = time.time()

                    for unit in units:
                        if unit.canAct():
                            if is_opponent:
                                # Call the opponent directly for unit decision
                                self.actionBuffer.append( self.agents[team].decide_action(unit.id, None, unit.team, newTurn) )
                            elif self.agents[team] == None:
                                # RL training agent that is controlling the simulation
                                # The enviornment then handles this unit, and calls take_action() to buffer an requested action
                                yield (unit.id, None, unit.team, newTurn)
                            else:
                                raise Exception("Invalid agent type. Should be None for the training agent or inherit from 'AgentOpponent' for an opponent.")
                            newTurn = False
                    
                    cities = self.state["teamStates"][team]["cities"]
                    for city in cities:
                        for city_tile in city.citytiles:
                            if city_tile.canAct():
                                if is_opponent:
                                    # Call the opponent directly for unit decision
                                    self.actionBuffer.append( self.agents[team].decide_action(None, city_tile.id, city_tile.team, newTurn) )
                                elif self.agents[team] == None:
                                    # RL training agent that is controlling the simulation
                                    # The enviornment then handles this city, and calls take_action() to buffer an requested action
                                    yield (None, city_tile.id, city_tile.team, newTurn)
                                else:
                                    raise Exception("Invalid agent type. Should be None for the training agent or inherit from 'AgentOpponent' for an opponent.")
                                newTurn = False
                    
                    actionsTimeTaken[team] = time.time() - start_time
                
                print("Time taken per agent for turn: (%.3fs, %.3fs)", actionsTimeTaken[0], actionsTimeTaken[1])
                
                # Now let the game actually process the requested actions and play the turn
                game_over = not self.game.runTurnWithActions(self.actionBuffer)
                self.actionBuffer = []


class LuxEnvironment(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def takeAction(self, action):
        '''TODO: Take action'''
        pass
    
    def __init__(self, configs, opponentAgent):
        super(LuxEnvironment, self).__init__()

        # Create the game
        self.game = Game(configs, agents = [self.agent, self.agentOpponent])
        self.matchController = MatchController( self.game, agents =[None, AgentOpponent()] )
        self.matchGenerator = self.matchController.run_to_next_observation()

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space_map = [
            partial(MoveAction,direction=Constants.DIRECTIONS.CENTER), # This is the do-nothing action
            partial(MoveAction,direction=Constants.DIRECTIONS.NORTH),
            partial(MoveAction,direction=Constants.DIRECTIONS.WEST),
            partial(MoveAction,direction=Constants.DIRECTIONS.SOUTH),
            partial(MoveAction,direction=Constants.DIRECTIONS.EAST),
            #TransferAction,
            SpawnWorkerAction,
            SpawnCityAction,
            #ResearchAction,
            #PillageAction,
        ]
        self.action_space = spaces.Discrete(len(self.action_space_map))

        # Example super-basic discrete observation space
        self.observation_space_map = [
            # State observations
            partial(isNight, self),
            
            # Unit observations, empty if not a unit
            partial(cargoAmount, self),

            partial(nearestWoodDistance, self),
            partial(nearestWoodDirection, self),

            partial(nearestCityDistance, self),
            partial(nearestCityDirection, self),
            partial(nearestCityFuel, self),
            partial(nearestCitySize, self),
            partial(nearestCityUpkeep, self),

            # City observations, empty if not a city
            partial(cityFuel, self),
            partial(citySize, self),
            partial(cityUpkeep, self),
        ]

        self.observation_space(spaces.Discrete(len(self.observation_space_map)))

        # Example for using image as input instead:
        #self.observation_space = spaces.Box(low=0, high=255, shape=
        #                (map_height, map_width, 10), dtype=np.uint8)

        self.reset()
    
    def _next_observation(self):
        # Get the next observation
        (unitid, citytileid, team, isNewTurn) = next(self.matchGenerator)

        if isNewTurn:
            # It's a new turn this event. This flag is set True for only the first observation from each turn.
            # Update any per-turn fixed observation space that doesn't change per unit/city controlled.
            pass
        
        # TODO: Call the observation space functions
        return np.array(np.zeros( self.observation_space.shape ) )

    def _take_action(self, action):
        self.game.take_action(action)
        pass

    def _reward(self):
        # TODO: Returns the reward function for this agent.
        return 0.0

    def step(self, action):
        # Take this action, then get the state at the next action
        self._take_action(action) # Decision for 1 unit
        self.current_step += 1

        # Calculate reward for this step
        reward = self._reward()

        # TODO: Logic for when the game ends
        done = False
        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self):
        self.current_step = 0

        # Reset game + map
        self.matchController.reset()

        return self._next_observation()

    def render(self):
        print(self.current_step)
        print(self.game.map.getMapString())

