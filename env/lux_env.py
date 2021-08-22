import random
import json
import gym
from gym import spaces
import numpy as np

N_DISCRETE_ACTIONS = 10

class LuxPerUnitEnvironment(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def takeAction(self, action):
        '''TODO: Take action'''
        pass

    def __init__(self, map_height, map_width):
        super(LuxPerUnitEnvironment, self).__init__()

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)

        # Example for using image as input:
        self.observation_space = spaces.Box(low=0, high=255, shape=
                        (map_height, map_width, 10), dtype=np.uint8)
        self.reset()
    
    def _next_observation(self):
        # Get the next observation
        return np.array(np.zeros( self.observation_space.shape ) )

    def _take_action(self, action):
        # TODO: Apply the action on the state of the game
        pass

    def _reward(self):
        # TODO: Returns the reward function for this agent.
        return 0.0

    def step(self, action):
        # Execute one time step within the environment
        self._take_action(action)
        self.current_step += 1

        # Calculate reward for this step
        reward = self._reward()

        # TODO: Logic for when the game ends
        done = False

        # Get next observation
        obs = self._next_observation() 

        return obs, reward, done, {}

    def reset(self):
        self.current_step = 0

        # TODO: Reset game + map

        return self._next_observation()

    def render(self):
        print(self.current_step)

