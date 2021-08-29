''' Implements the base class for a training Agent '''
from ..game.game import Game
from ..game.match_controller import MatchController
from ..game.actions import *
from ..game.constants import Constants

import gym
from gym import spaces
import numpy as np
from functools import partial # pip install functools

class LuxEnvironment(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def takeAction(self, action):
        '''TODO: Take action'''
        pass
    
    def __init__(self, configs, opponentAgent):
        super(LuxEnvironment, self).__init__()

        # Create the game
        self.game = Game(configs)
        self.matchController = MatchController( self.game, agents =[None, opponentAgent] )
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
        '''self.observation_space_map = [
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

        self.observation_space = spaces.Discrete(len(self.observation_space_map)))'''
        self.observation_space = spaces.Discrete(10)

        # Example for using image as input instead:
        #self.observation_space = spaces.Box(low=0, high=255, shape=
        #                (game.map.width, game.map.height, 10), dtype=np.uint8)

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
        self.matchController.take_action(action)
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
