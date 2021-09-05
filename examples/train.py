from luxai2021.game.game_constants import GAME_CONSTANTS
from luxai2021.game.position import Position
import gym
from gym import spaces
import numpy as np
from collections import OrderedDict

import argparse
import random

import time
import json
import datetime as dt
import os

from stable_baselines3 import PPO # pip install stable-baselines3
from luxai2021.env.lux_env import LuxEnvironment
from luxai2021.env.agent import Agent
from luxai2021.game.constants import LuxMatchConfigs_Default
from luxai2021.game.actions import *
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback

from functools import partial # pip install functools
from typing import Callable


# https://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
def closest_node(node, nodes):
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)

# https://stable-baselines3.readthedocs.io/en/master/guide/examples.html?highlight=SubprocVecEnv#multiprocessing-unleashing-the-power-of-vectorized-environments
def make_env(env, rank, seed=0):
    """
    Utility function for multiprocessed env.

    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env.seed(seed + rank)
        return env
    set_random_seed(seed)
    return _init

def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    Linear learning rate schedule.

    :param initial_value: Initial learning rate.
    :return: schedule that computes
      current learning rate depending on remaining progress
    """
    def func(progress_remaining: float) -> float:
        """
        Progress will decrease from 1 (beginning) to 0.

        :param progress_remaining:
        :return: current learning rate
        """
        return progress_remaining * initial_value

    return func

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

        # Observation space: (Basic minimum for a miner agent)
        # Object:
        #   5x direction_nearest_wood
        #   1x distance_nearest_wood
        #   1x amount
        #
        #   5x direction_nearest_coal
        #   1x distance_nearest_coal
        #   1x amount
        #
        #   5x direction_nearest_uranium
        #   1x distance_nearest_uranium
        #   1x amount
        #
        #   5x direction_nearest_city
        #   1x distance_nearest_city
        #   1x amount of fuel
        #
        #   5x direction_nearest_worker
        #   1x distance_nearest_worker
        #   1x amount of cargo
        # Unit:
        #   1x cargo size
        # State:
        #   1x is night
        #   1x percent of game done
        #   2x citytile counts [cur player, opponent]
        #   2x worker counts [cur player, opponent]
        #   2x cart counts [cur player, opponent]
        self.observation_shape = (7*5+1+1+1+2+2+2, )
        self.observation_space = spaces.Box(low=0, high=1, shape=
                        self.observation_shape, dtype=np.float16)


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
                for u in game.state["teamStates"][team]["units"].values():
                    key = str(u.type)
                    if t != team:
                        key = str(u.type) + "_opponent"
                    
                    if key not in self.objectNodes:
                        self.objectNodes[key] = np.array([[u.pos.x, u.pos.y]])
                    else:
                        self.objectNodes[key] = np.concatenate(
                            (
                                self.objectNodes[key],
                                [[u.pos.x, u.pos.y]]
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

        # Observation space: (Basic minimum for a miner agent)
        # Object:
        #   5x direction_nearest_wood
        #   1x distance_nearest_wood
        #   1x amount
        #
        #   5x direction_nearest_coal
        #   1x distance_nearest_coal
        #   1x amount
        #
        #   5x direction_nearest_uranium
        #   1x distance_nearest_uranium
        #   1x amount
        #
        #   5x direction_nearest_city
        #   1x distance_nearest_city
        #   1x amount of fuel
        #
        #   5x direction_nearest_worker
        #   1x distance_nearest_worker
        #   1x amount of cargo
        # Unit:
        #   1x cargo size
        # State:
        #   1x is night
        #   1x percent of game done
        #   2x citytile counts [cur player, opponent]
        #   2x worker counts [cur player, opponent]
        #   2x cart counts [cur player, opponent]
        obs = np.zeros(self.observation_shape)
        pos = None
        if unit != None:
            pos = unit.pos
        else:
            pos = citytile.pos

        if pos == None:
            obsIndex = 7 * 5
        else:
            # Encode the direction to the nearest objects
            #   5x direction_nearest
            #   1x distance
            for key in [
                Constants.RESOURCE_TYPES.WOOD,
                Constants.RESOURCE_TYPES.COAL,
                Constants.RESOURCE_TYPES.URANIUM,
                "city",
                str(Constants.UNIT_TYPES.WORKER)]:
                # Process the direction to and distance to this object type
                
                # Encode the direction to the nearest object (excluding itself)
                #   5x direction
                #   1x distance
                if key in self.objectNodes:
                    if (
                            (key == "city" and citytile != None) or
                            (unit != None and unit.type == key)
                        ):
                        # Filter out the current unit from the closest-search
                        closestIndex = closest_node((pos.x, pos.y), self.objectNodes[key])
                        filteredNodes = np.delete(self.objectNodes[key], closestIndex, axis=0)
                    else:
                        filteredNodes = self.objectNodes[key]
                    
                    if len(filteredNodes) == 0:
                        # No other object of this type
                        obs[obsIndex+5] = 1.0
                    else:
                        # There is another object of this type
                        closestIndex = closest_node((pos.x, pos.y), filteredNodes)
                        
                        if closestIndex != None and closestIndex >= 0:
                            closest = filteredNodes[closestIndex]
                            closestPosition = Position(closest[0], closest[1])
                            direction = pos.directionTo( closestPosition )
                            mapping = {
                                Constants.DIRECTIONS.CENTER: 0,
                                Constants.DIRECTIONS.NORTH: 1,
                                Constants.DIRECTIONS.WEST: 2,
                                Constants.DIRECTIONS.SOUTH: 3,
                                Constants.DIRECTIONS.EAST: 4,
                            }
                            obs[obsIndex+mapping[direction]] = 1.0 # One-hot encoding direction

                            # 0 to 1 distance
                            distance = pos.distanceTo( closestPosition )
                            obs[obsIndex+5] = min(distance / 20.0, 1.0)

                            # 0 to 1 value (amount of resource, cargo for unit, or fuel for city)
                            if key == "city":
                                # City fuel
                                obs[obsIndex+6] = min(
                                    game.cities[game.map.getCellByPos(closestPosition).citytile.cityid].fuel / 300,
                                    1.0
                                )
                            elif key in [Constants.RESOURCE_TYPES.WOOD, Constants.RESOURCE_TYPES.COAL, Constants.RESOURCE_TYPES.URANIUM]:
                                # Resource amount
                                obs[obsIndex+6] = min(
                                    game.map.getCellByPos(closestPosition).resource.amount / 500,
                                    1.0
                                )
                            else:
                                # Unit cargo
                                obs[obsIndex+6] = min(
                                    next(iter(game.map.getCellByPos(closestPosition).units.values())).getCargoSpaceLeft() / 100,
                                    1.0
                                )

                obsIndex += 7
            
        
        if unit != None:
            # Encode the cargo space
            #   1x cargo size
            obs[obsIndex] = unit.getCargoSpaceLeft() / GAME_CONSTANTS["PARAMETERS"]["RESOURCE_CAPACITY"]["WORKER"]
            obsIndex += 1
        else:
            obsIndex += 1
        
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

    def getReward(self, game, isGameFinished, isNewTurn, isGameError):
        """
        Returns the reward function for this step of the game.
        """
        if isGameError:
            # Game environment step failed, assign a game lost reward to not incentivise this
            print("Game failed due to error")
            return -1.0

        if not isNewTurn and not isGameFinished:
            # Only apply rewards at the start of each turn
            return 0

        
        # Get some basic stats
        unitCount = len(game.state["teamStates"][(self.team)%2]["units"])
        unitCountOpponent = len(game.state["teamStates"][(self.team+1)%2]["units"])
        cityCount = 0
        cityCountOpponent = 0
        cityTileCount = 0
        cityTileCountOpponent = 0
        for city in game.cities.values():
            if city.team == self.team:
                cityCount += 1
            else:
                cityCountOpponent += 1
            
            for cell in city.citycells:
                if city.team == self.team:
                    cityTileCount += 1
                else:
                    cityTileCountOpponent += 1
        
        # Give a reward each turn for each tile and unit alive each turn
        rewardState = cityTileCount*0.01 + unitCount*0.001
        
        if isGameFinished:
            # Get some basic stats
            unitCount = len(game.state["teamStates"][(self.team)%2]["units"])
            unitCountOpponent = len(game.state["teamStates"][(self.team+1)%2]["units"])
            cityCount = 0
            cityCountOpponent = 0
            cityTileCount = 0
            cityTileCountOpponent = 0
            for city in game.cities.values():
                if city.team == self.team:
                    cityCount += 1
                else:
                    cityCountOpponent += 1
                
                for cell in city.citycells:
                    if city.team == self.team:
                        cityTileCount += 1
                    else:
                        cityTileCountOpponent += 1
            
            print("\tUnits: %i, %i" % (unitCount, unitCountOpponent))
            print("\tCities: %i, %i" % (cityCount, cityCountOpponent))
            print("\tCityTiles: %i, %i" % (cityTileCount, cityTileCountOpponent))

            # Give a bigger reward for end-of-game unit and city count
            if game.getWinningTeam() == self.team:
                print("Won match")
                return rewardState*500
            else:
                print("Lost match")
                return rewardState*500
        else:
            # Calculate the current reward state
            # If you want, any micro rewards or other rewards that are not win/lose end-of-game rewards
            return rewardState
            

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
                actionCode, _states = self.model.predict(obs, deterministic=True)
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
                        actionCode, _states = self.model.predict(obs, deterministic=True)
                        if actionCode != None:
                            actions.append(self.actionCodeToAction(actionCode, game=game, unit=None, citytile=citytile, team=city.team))
                        newTurn = False

        timeTaken = time.time() - startTime
        if timeTaken > 0.5: # Warn if larger than 0.5 seconds.
            print("WARNING: Inference took %.3f seconds for computing actions. Limit is 1 second." % (timeTaken))
        
        return actions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Training script for Lux RL agent.')
    parser.add_argument('--id', help='Identifier of this run', type=str)
    parser.add_argument('--learning_rate', help='Learning rate', type=float)
    parser.add_argument('--gamma', help='Gamma', type=float)
    parser.add_argument('--gae_lambda', help='GAE Lambda', type=float)
    parser.add_argument('--batch_size', help='batch_size', type=float)
    args = parser.parse_args()
    print(args)

    configs = LuxMatchConfigs_Default

    # Create a default opponent agent
    opponent = Agent()

    # Create a RL agent in training mode
    player = AgentPolicy(mode="train")
    
    # Train the model
    #num_cpu = 4
    #env = SubprocVecEnv([make_env(LuxEnvironment(configs, learningAgent=AgentPolicy(mode="train"), opponentAgent=Agent()), i) for i in range(num_cpu)])
    id = str(random.randint(0,10000)) if not args.id else args.id
    print("Run id %s" % id)
    env = LuxEnvironment(configs, player, opponent)
    model = PPO("MlpPolicy",
        env,
        verbose=1,
        tensorboard_log="./lux_tensorboard/",
        #learning_rate = args.learning_rate if args.learning_rate else 0.001,
        learning_rate=linear_schedule(args.learning_rate if args.learning_rate else 0.001),
        gamma = args.gamma if args.gamma else 0.995,
        gae_lambda = args.gae_lambda if args.gae_lambda else 0.95,
        batch_size = args.batch_size if args.batch_size else 64,
        n_steps=2048*4
    )

    print("Training model...")
    # Save a checkpoint every 1M steps
    checkpointCallback = CheckpointCallback(save_freq=1000000, save_path='./models/',
                                         name_prefix='rl_model_%s' % str(id))
    model.learn(total_timesteps=20000000, callback=checkpointCallback) # 20M steps
    print("Done training model.")
    
    # Inference the model
    print("Inferencing model policy with rendering...")
    obs = env.reset()
    for i in range(600):
        actionCode, _states = model.predict(obs, deterministic=True)
        obs, rewards, done, info = env.step(actionCode)
        if i % 5 == 0:
            print("Turn %i" % i)
            env.render()

        if done:
            print("Episode done, resetting.")
            obs = env.reset()
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
    
