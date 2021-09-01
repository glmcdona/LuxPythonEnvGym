import random
import time
import gym
from gym import spaces
import numpy as np
from .game import Game
from .actions import *
from .constants import Constants
from ..env.agent import Agent


class MatchController():
    def __init__(self, game, agents = [None, None]) -> None:
        self.actionBuffer = []
        self.game = game
        self.agents = agents
        if len(agents) != 2:
            raise ValueError("Two agents must be specified.")

        # Validate the agents
        self.trainingAgentCount = 0
        for i, agent in enumerate(agents):
            if not (issubclass(type(agent),Agent) or isinstance(agent,Agent)):
                raise ValueError("All agents must inherit from Agent.")
            if agent.getAgentType == Constants.AGENT_TYPE.LEARNING:
                self.trainingAgentCount += 1

            # Initialize agent
            agent.setTeam(i)
            agent.setController(self)

        if self.trainingAgentCount > 1:
            raise ValueError("At most one agent must be trainable.")
        elif self.trainingAgentCount == 1:
            print("Running in training mode.")
        elif self.trainingAgentCount == 0:
            print("Running in inference-only mode.")
    
    def reset(self):
        # Reset the game
        self.game.reset()
        self.actionBuffer = []

        # Randomly re-assign teams of the agents
        r = random.randint(0,1)
        self.agents[0].setTeam(r)
        self.agents[1].setTeam((r+1)%2)

    def takeAction(self, action):
        """ Adds the specified action to the action buffer """
        if action is not None:
            # Validate the action
            if action.isValid(self.game):
                # Add the action
                self.actionBuffer.append(action)

    def takeActions(self, actions):
        """ Adds the specified action to the action buffer """
        for action in actions:
            self.takeAction(action)
    
    def runToNextObservation(self):
        """ 
            Generator function that gets the observation at the next Unit/City
            to be controlled.
            Returns: tuple describing the unit who's control decision is for (unitid, city, team, is new turn)
        """
        gameOver = False
        while not gameOver:
            # Process this turn
            for agent in self.agents:
                if agent.getAgentType() == Constants.AGENT_TYPE.AGENT:
                    # Call the agent for the set of actions
                    actions = agent.processTurn(self.game, agent.team)
                    self.takeActions(actions)
                elif agent.getAgentType() == Constants.AGENT_TYPE.LEARNING:
                    # Yield the game to make a decision, since the learning environment is the function caller
                    newTurn = True
                    startTime = time.time()

                    units = self.game.state["teamStates"][agent.team]["units"].values()
                    for unit in units:
                        if unit.canAct():
                            # RL training agent that is controlling the simulation
                            # The enviornment then handles this unit, and calls take_action() to buffer a requested action
                            yield (unit, None, unit.team, newTurn)
                            newTurn = False
                    
                    cities = self.game.cities.values()
                    for city in cities:
                        if city.team == agent.team:
                            for cell in city.citycells:
                                citytile = cell.citytile
                                if citytile.canAct():
                                    # RL training agent that is controlling the simulation
                                    # The enviornment then handles this city, and calls take_action() to buffer a requested action
                                    yield (None, citytile, citytile.team, newTurn)
                                    newTurn = False
                    
                    timeTaken = time.time() - startTime
                    if timeTaken > 0.5: # Warn if larger than 0.5 seconds.
                        print("WARNING: Turn took %.3f seconds for computing actions. Limit is 1 second." % (timeTaken))
            
            # Now let the game actually process the requested actions and play the turn
            gameOver = self.game.runTurnWithActions(self.actionBuffer)
            self.actionBuffer = []

