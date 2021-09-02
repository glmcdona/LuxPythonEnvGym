from luxai2021.game.game_constants import GAME_CONSTANTS
from luxai2021.game.position import Position
import gym
from gym import spaces
import numpy as np
from collections import OrderedDict

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

import torch as th
from torch import nn

from stable_baselines3.common.torch_layers import BaseFeaturesExtractor



# Custom policy network for the shared feature extraction forward
# https://stable-baselines3.readthedocs.io/en/master/guide/custom_policy.html
class CustomCombinedExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.spaces.Dict):
        # We do not know features-dim here before going over all the items,
        # so put something dummy for now. PyTorch requires calling
        # nn.Module.__init__ before adding modules
        super(CustomCombinedExtractor, self).__init__(observation_space, features_dim=1)

        extractors = {}

        total_concat_size = 0
        # We need to know size of the output of this extractor,
        # so go over all the spaces and compute output feature sizes
        for key, subspace in observation_space.spaces.items():
            if key.startswith("map") and isinstance(subspace, spaces.Box):
                # Downsample the map. Assumes it is 32x32 for the largest map support. The smallest mapsize of 12x12 is commended for information sake.
                #NOTE: Color channels are in subspace.shape[0] and it is 1
                input_width = subspace.shape[1]
                input_height = subspace.shape[2]
                input_channels = subspace.shape[3]
                filter_count = 32
                print(subspace.shape)

                extractors[key] = nn.Sequential(
                    # 3x3x[num of map layers]. Largest map goes from [32x32xNCHANNELS] down to [32x32xNFILTERS]
                    # Num parameters for layer = 3x3x11x32 = 3,168
                    nn.Conv3d(subspace.shape[0], filter_count, kernel_size=(3,3,input_channels), padding=(2,2,0)), 
                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.ReLU(),
                    nn.MaxPool3d (kernel_size=(2,2,1)), # largest map (32x32xNFILTERS -> 16x16) or smallest map (12x12) -> (6x6)

                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.ReLU(),
                    nn.MaxPool3d (kernel_size=(2,2,1)), # largest map (32x32xNFILTERS -> 8x8xNFILTERS) or smallest map (12x12xNFILTERS) -> (3x3xNFILTERS)

                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.Conv3d(filter_count, filter_count, kernel_size=(3,3,1), padding='same'),
                    nn.ReLU(),
                    nn.Flatten(),
                )
                print(extractors[key])
                print("Flattened size from CNN: %i" % ((input_width // 2 // 2) * (input_height // 2 // 2) * filter_count))
                total_concat_size += (input_width // 2 // 2) * (input_height // 2 // 2) * filter_count
            elif isinstance(subspace, spaces.Box):
                # Run through a simple MLP
                extractors[key] = nn.Flatten()
                total_concat_size += np.prod(subspace.shape) # Multiply all the axes together to get total size?
            elif isinstance(subspace, spaces.Discrete):
                # Run through a simple MLP
                extractors[key] = nn.Flatten()
                total_concat_size += subspace.n

        self.extractors = nn.ModuleDict(extractors)

        # Update the features dim manually
        self._features_dim = total_concat_size

    def forward(self, observations) -> th.Tensor:
        encoded_tensor_list = []

        # self.extractors contain nn.Modules that do all the processing.
        for key, extractor in self.extractors.items():
            encoded_tensor_list.append(extractor(observations[key]))
        # Return a (B, self._features_dim) PyTorch tensor, where B is batch dimension.
        return th.cat(encoded_tensor_list, dim=1)


# https://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
def closest_node(node, nodes):
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)

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
            #partial(TransferAction,direction=Constants.DIRECTIONS.NORTH),
            #partial(TransferAction,direction=Constants.DIRECTIONS.WEST),
            #partial(TransferAction,direction=Constants.DIRECTIONS.SOUTH),
            #partial(TransferAction,direction=Constants.DIRECTIONS.EAST),
            SpawnWorkerAction,
            SpawnCityAction,
            #ResearchAction,
            #PillageAction,
        ]
        self.action_space = spaces.Discrete(len(self.actionSpaceMap))

        # Observation space: (Basic minimum for a wood miner agent)
        # Unit:
        #   5x direction_nearest_wood
        #   5x direction_nearest_city
        #   1x cargo size
        # State:
        #   1x is night
        #   1x percent of game done
        #   2x citytile counts [cur player, opponent]
        #   2x worker counts [cur player, opponent]
        #   2x cart counts [cur player, opponent]
        self.observation_space_dict = {
            #  Unit specific observations
            "unit_direction_nearest_wood": spaces.Discrete(5),
            "unit_direction_nearest_city": spaces.Discrete(5),
            "unit_cargo": spaces.Box(low=0, high=1, shape=(1,)),

            # Game state observations
            "game_is_night": spaces.Discrete(2),
            "game_percent_done": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float16),
            "game_citytile_counts": spaces.Box(low=0, high=1, shape=(2,), dtype=np.float16),
            "game_worker_counts": spaces.Box(low=0, high=1, shape=(2,), dtype=np.float16),
            "game_cart_counts": spaces.Box(low=0, high=1, shape=(2,), dtype=np.float16),

            # Map of the game, organize as maximum map size (32x32xnum_layers)
            # Layers: 11x
            #   OpponentCarts
            #   OpponentCities
            #   OpponentWorkers
            #   MyCarts
            #   MyCities
            #   MyWorkers
            #   CityFuelOrUnitCargo
            #   Cooldown
            #   Resources: Wood
            #   Resources: Coal
            #   Resources: Uranium
            #   RoadLevel
            "map": spaces.Box(low=0, high=1, shape=(1, 32, 32, 11), dtype=np.float16) # 32x32x11 = 11,264
        }

        self.observation_space = spaces.Dict(self.observation_space_dict)


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
        obsIndex = 0
        if isNewTurn:
            # It's a new turn this event. This flag is set True for only the first observation from each turn.
            # Update any per-turn fixed observation space that doesn't change per unit/city controlled.

            # Build a list of object nodes by type for quick distance-searches
            self.objectNodes = {}

            # Add resources
            for cell in game.map.resources:
                if cell.resource.type not in self.objectNodes:
                    self.objectNodes[cell.resource.type] = np.array([[cell.pos.x, cell.pos.y]])
                else:
                    self.objectNodes[cell.resource.type] = np.concatenate(
                        (
                            self.objectNodes[cell.resource.type],
                            [[cell.pos.x, cell.pos.y]]
                        )
                        , axis=0
                    )
            
            # Add your own and opponent units
            for t in [team, (team+1)%2]:
                for unit in game.state["teamStates"][team]["units"].values():
                    key = str(unit.type)
                    if t != team:
                        key = str(unit.type) + "_opponent"
                    
                    if key not in self.objectNodes:
                        self.objectNodes[key] = np.array([[unit.pos.x, unit.pos.y]])
                    else:
                        self.objectNodes[key] = np.concatenate(
                            (
                                self.objectNodes[key],
                                [[unit.pos.x, unit.pos.y]]
                            )
                            , axis=0
                        )
            
            # Add your opponent units
            for unit in game.state["teamStates"][(team+1)%2]["units"].values():
                key = str(unit.type) + "_opponent"
                if key not in self.objectNodes:
                    self.objectNodes[key] = np.array([[unit.pos.x, unit.pos.y]])
                else:
                    self.objectNodes[key] = np.concatenate(
                        (
                            self.objectNodes[key],
                            [[unit.pos.x, unit.pos.y]]
                        )
                        , axis=0
                    )
            
            # Add your own and opponent cities
            for city in game.cities.values():
                for cells in city.citycells:
                    key = "city"
                    if city.team != team:
                        key = "city_opponent"
                    
                    if key not in self.objectNodes:
                        self.objectNodes[key] = np.array([[cells.pos.x, cells.pos.y]])
                    else:
                        self.objectNodes[key] = np.concatenate(
                            (
                                self.objectNodes[key],
                                [[cells.pos.x, cells.pos.y]]
                            )
                            , axis=0
                        )

        # Observation space: (Basic minimum for a wood miner agent)
        obs = OrderedDict(
            [
                ("unit_direction_nearest_wood", 0), # "unit_direction_nearest_wood": spaces.Discrete(5),
                ("unit_direction_nearest_city", 0), # "unit_direction_nearest_city": spaces.Discrete(5),
                ("unit_cargo", np.zeros((1,))),     # "unit_cargo": spaces.Box(low=0, high=1, shape=(1,)),
                ("game_is_night", 0),               # "game_is_night": spaces.Discrete(2),
                ("game_percent_done", np.zeros((1,))), # "game_percent_done": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float16),
                ("game_citytile_counts", np.zeros((2,))), # "game_citytile_counts": spaces.Box(low=0, high=1, shape=(2,), dtype=np.float16),
                ("game_worker_counts", np.zeros((2,))),
                ("game_cart_counts", np.zeros((2,))),
                ("map", np.zeros((1,32,32,11))), # "map": spaces.Box(low=0, high=1, shape=(32, 32, 11), dtype=np.float16) # 32x32x11 = 11,264
            ]
        )
        return obs

        #  Unit specific observations
        if unit != None:
            # Encode the direction to the nearest wood
            #   5x direction_nearest_wood
            if Constants.RESOURCE_TYPES.WOOD in self.objectNodes:
                closestWoodIndex = closest_node((unit.pos.x, unit.pos.y), self.objectNodes[Constants.RESOURCE_TYPES.WOOD])
                if closestWoodIndex != None and closestWoodIndex >= 0:
                    closestWood = self.objectNodes[Constants.RESOURCE_TYPES.WOOD][closestWoodIndex]
                    direction = unit.pos.directionTo( Position(closestWood[0], closestWood[1]) )
                    mapping = {
                        Constants.DIRECTIONS.CENTER: 0,
                        Constants.DIRECTIONS.NORTH: 1,
                        Constants.DIRECTIONS.WEST: 2,
                        Constants.DIRECTIONS.SOUTH: 3,
                        Constants.DIRECTIONS.EAST: 4,
                    }
                    obs[mapping[direction]] = 1.0 # One-hot encoding
            obsIndex += 5

            # Encode the direction to the nearest city
            #   5x direction_nearest_city
            if "city" in self.objectNodes:
                closestCityIndex = closest_node((unit.pos.x, unit.pos.y), self.objectNodes["city"])
                if closestCityIndex != None and closestCityIndex >= 0:
                    closestCity = self.objectNodes["city"][closestCityIndex]
                    direction = unit.pos.directionTo( Position(closestCity[0], closestCity[1]) )
                    mapping = {
                        Constants.DIRECTIONS.CENTER: 0,
                        Constants.DIRECTIONS.NORTH: 1,
                        Constants.DIRECTIONS.WEST: 2,
                        Constants.DIRECTIONS.SOUTH: 3,
                        Constants.DIRECTIONS.EAST: 4,
                    }
                    obs[obsIndex+mapping[direction]] = 1.0 # One-hot encoding
            obsIndex += 5

            # Encode the cargo space
            #   1x cargo size
            obs[obsIndex] = unit.getCargoSpaceLeft() / GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["WORKER"]
            obsIndex += 1
        else:
            obsIndex += 11
        
        # Game state observations
        #   1x is night
        obs[obsIndex] = game.isNight()
        obsIndex += 1
        #   1x percent of game done
        obs[obsIndex] = game.state["turn"] / GAME_CONSTANTS["PARAMETERS"]["MAX_DAYS"]
        obsIndex += 1
        #   2x citytile counts [cur player, opponent]
        #   2x worker counts [cur player, opponent]
        #   2x cart counts [cur player, opponent]
        maxCount = 30
        for key in ["city", str(Constants.UNIT_TYPES.WORKER), str(Constants.UNIT_TYPES.CART)]:
            if key in self.objectNodes:
                obs[obsIndex] = len(self.objectNodes[key]) / maxCount
            if (key + "_opponent") in self.objectNodes:
                obs[obsIndex+1] = len(self.objectNodes[(key + "_opponent")]) / maxCount
            obsIndex += 2

        return obs

    def actionCodeToAction(self, actionCode, game, unit=None, citytile=None, team=None):
        """
        Takes an action in the environment according to actionCode:
            actionCode: Index of action to take into the action array.
        Returns: An action.
        """
        # Map actionCode index into to a constructed Action object
        try:
            x = None
            y = None
            if citytile != None:
                x = citytile.pos.x
                y = citytile.pos.y
            elif unit != None:
                x = unit.pos.x
                y = unit.pos.y

            return self.actionSpaceMap[actionCode](
                game = game,
                unitid = unit.id if unit else None,
                unit = unit,
                cityid = citytile.cityid if citytile else None,
                citytile = citytile,
                team = team,
                x = x,
                y = y
            )
        except Exception as e:
            # Not a valid action
            print(e)
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
    policy_kwargs = dict(
        features_extractor_class=CustomCombinedExtractor
    )
    model = PPO("MlpPolicy",
        env,
        verbose=1,
        tensorboard_log="./lux_tensorboard/",
        learning_rate = 0.0001,
        gamma=0.995,
        gae_lambda = 0.95,
        policy_kwargs=policy_kwargs
    )
    print("Training model...")
    model.learn(total_timesteps=10000000)
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
    model = PPO("MlpPolicy",
        env,
        verbose=1,
        tensorboard_log="./lux_tensorboard/",
        learning_rate = 0.0003,
        gamma=0.999,
        gae_lambda = 0.95
    )

    model.learn(total_timesteps=2000)
    env.close()
    print("Done")
