import gym
from gym import spaces
import numpy as np

import time
import json
import datetime as dt
import os

from stable_baselines3 import PPO # pip install stable-baselines3
from luxai2021.env.lux_env import LuxEnvironment
from luxai2021.env.agent import Agent
from luxai2021.game.constants import LuxMatchConfigs_Default
from luxai2021.game.actions import *

from functools import partial # pip install functools

class AgentPolicy(Agent):
    def __init__(self, mode="train", model=None) -> None:
        """
        Arguments:
            mode: "train" or "inference", which controls if this agent is for training or not.
            model: The pretrained model, or if None it will operate in training mode.
        """
        self.model = model
        self.mode = mode

        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.actionSpaceMap = [
            partial(MoveAction,direction=Constants.DIRECTIONS.CENTER), # This is the do-nothing action
            partial(MoveAction,direction=Constants.DIRECTIONS.NORTH),
            partial(MoveAction,direction=Constants.DIRECTIONS.WEST),
            partial(MoveAction,direction=Constants.DIRECTIONS.SOUTH),
            partial(MoveAction,direction=Constants.DIRECTIONS.EAST),
            #TransferAction,
            #SpawnWorkerAction,
            #SpawnCityAction,
            #ResearchAction,
            #PillageAction,
        ]
        self.action_space = spaces.Discrete(len(self.actionSpaceMap))

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
        #self.observationSpace = spaces.Box(low=0, high=255, shape=
        #                (game.map.width, game.map.height, 10), dtype=np.uint8)


    def getAgentType(self):
        """
        Returns the type of agent. Use AGENT for inference, and LEARNING for training a model.
        """
        if self.mode == "train":
            return Constants.AGENT_TYPE.LEARNING
        else:
            return Constants.AGENT_TYPE.AGENT
    
    def getObservation(self, game, unit, citytile, team, isNewTurn):
        """
        Implements getting a observation from the current game for this unit or city
        """
        if isNewTurn:
            # It's a new turn this event. This flag is set True for only the first observation from each turn.
            # Update any per-turn fixed observation space that doesn't change per unit/city controlled.
            pass
        
        return np.array(np.zeros( self.observation_space.shape ) )

    def actionCodeToAction(self, actionCode, game, unit=None, citytile=None, team=None):
        """
        Takes an action in the environment according to actionCode:
            actionCode: Index of action to take into the action array.
        Returns: An action.
        """
        # Map actionCode index into to a constructed Action object
        try:
            return self.actionSpaceMap[actionCode](
                game=game,
                unitid=unit.id if unit else None,
                unit=unit,
                cityid = citytile.cityid if citytile else None,
                citytile=citytile,
                team=team
            )
        except Exception as e:
            # Not a valid action
            return None

    def takeAction(self, actionCode, game, unit=None, citytile=None, team=None):
        """
        Takes an action in the environment according to actionCode:
            actionCode: Index of action to take into the action array.
        """
        action = self.actionCodeToAction( actionCode, game, unit, citytile, team )
        self.matchController.takeAction( action )

    def getReward(self, game, isGameFinished, isNewTurn):
        """
        Returns the reward function for this step of the game.
        """
        if isGameFinished:
            # Give a reward of 1 or -1 based on if they won or not.
            if game.getWinningTeam() == self.team:
                print("Won match")
                return 1.0
            else:
                print("Lost match")
                return -1.0
        else:
            # If you want, any micro rewards or other rewards that are not win/lose end-of-game rewards
            return 0.0

    def processTurn(self, game, team):
        """
        Decides on a set of actions for the current turn. Not used in training, only inference.
        Returns: Array of actions to perform.
        """
        startTime = time.time()
        actions = []
        newTurn = True

        # Inference the model per-unit
        units = game.state["teamStates"][team]["units"].values()
        for unit in units:
            if unit.canAct():
                obs = self.getObservation(game, unit, None, unit.team, newTurn )
                actionCode, _states = self.model.predict(obs)
                if actionCode != None:
                    actions.append(self.actionCodeToAction(actionCode, game=game, unit=unit, citytile=None, team=unit.team))
                newTurn = False
        
        # Inference the model per-city
        cities = game.cities.values()
        for city in cities:
            if city.team == team:
                for cell in city.citycells:
                    citytile = cell.citytile
                    if citytile.canAct():
                        obs = self.getObservation(game, None, citytile, city.team, newTurn )
                        actionCode, _states = self.model.predict(obs)
                        if actionCode != None:
                            actions.append(self.actionCodeToAction(actionCode, game=game, unit=None, citytile=citytile, team=city.team))
                        newTurn = False

        timeTaken = time.time() - startTime
        if timeTaken > 0.5: # Warn if larger than 0.5 seconds.
            print("WARNING: Inference took %.3f seconds for computing actions. Limit is 1 second." % (timeTaken))
        
        return actions


if __name__ == "__main__":
    configs = LuxMatchConfigs_Default

    # Create a default opponent agent
    opponent = Agent()

    # Create a RL agent in training mode
    player = AgentPolicy(mode="train")

    # Train the model
    env = LuxEnvironment(configs, player, opponent)
    model = PPO("MlpPolicy", env, verbose=1)
    print("Training model...")
    model.learn(total_timesteps=20000)
    print("Done training model.")

    # Inference the model
    print("Inferencing model policy with rendering...")
    obs = env.reset()
    for i in range(400):
        actionCode, _states = model.predict(obs)
        obs, rewards, done, info = env.step(actionCode)
        if i % 50 == 0:
            print("Turn %i" % i)
            env.render()
        if done:
            print("Episode done, resetting.")
            obs = env.reset()
        env.close()
    print("Done")

    # Learn with self-play against the learned model as an opponent now
    print("Training model with self-play against last version of model...")
    player = AgentPolicy(mode="train")
    opponent = AgentPolicy(mode="inference", model=model)
    env = LuxEnvironment(configs, player, opponent)
    model = PPO("MlpPolicy", env, verbose=1)

    model.learn(total_timesteps=20000)
    env.close()
    print("Done")
