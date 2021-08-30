''' Implements the base class for a Lux enviornment '''
from ..game.game import Game
from ..game.match_controller import MatchController
from ..game.constants import Constants

import gym
from gym import spaces
import numpy as np



class LuxEnvironment(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}
    
    def __init__(self, configs, learningAgent, opponentAgent):
        super(LuxEnvironment, self).__init__()

        # Create the game
        self.game = Game(configs)
        self.matchController = MatchController( self.game, agents = [learningAgent, opponentAgent] )

        self.action_space = learningAgent.action_space
        self.observation_space = learningAgent.observation_space

        self.learningAgent = learningAgent

        self.current_step = 0
        self.matchGenerator = self.matchController.runToNextObservation()

    

    def step(self, action_code):
        # Take this action, then get the state at the next action
        #self._take_action(action) # Decision for 1 unit
        self.learningAgent.takeAction(action_code) # Decision for 1 unit
        self.current_step += 1

        # Get the next observation
        isNewTurn = True
        isGameOver = False
        try:
            (unitid, citytileid, team, isNewTurn) = next(self.matchGenerator)
            obs = self.learningAgent.getObservation(self.game, unitid, citytileid, team, isNewTurn)
        except StopIteration as err:
            # The game episode is done.
            isGameOver = True
            obs = None

        # Calculate reward for this step
        reward = self.learningAgent.getReward(self.game, isGameOver, isNewTurn)
        
        return obs, reward, isGameOver, {}

    def reset(self):
        self.current_step = 0

        # Reset game + map
        self.matchController.reset()
        self.matchGenerator = self.matchController.runToNextObservation()
        (unitid, citytileid, team, isNewTurn) = next(self.matchGenerator)

        obs = self.learningAgent.getObservation(self.game, unitid, citytileid, team, isNewTurn)

        return obs

    def render(self):
        print(self.current_step)
        print(self.game.map.getMapString())
