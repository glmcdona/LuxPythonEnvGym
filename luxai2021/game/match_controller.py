import time
from .game import Game
from .actions import *
from .constants import Constants


class AgentOpponent():
    def __init__(self) -> None:
        pass
    
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
        self.actionBuffer = []

    def take_action(self, action):
        """ Adds the specified action to the action buffer """
        if action is not None:
            self.actionBuffer.append(action)
    
    def run_to_next_observation(self):
        """ 
            Generator function that gets the observation at the next Unit/City
            to be controlled.
            Returns: tuple describing the unit who's control decision is for (unitid, city, team, is new turn)
        """
        game_over = False
        while not game_over:
            # Process this turn
            
            # Handle each team making decisions for their units and cities for this turn
            actionsTimeTaken = [0.0, 0.0] # Tracks the amount of time used per agent per turn
            for team in [Constants.TEAM.A, Constants.TEAM.B]:
                newTurn = True
                is_opponent = (self.agents[team] != None)
                #issubclass(self.agents[team], AgentOpponent) or isinstance(self.agents[team], AgentOpponent)
                units = self.game.state["teamStates"][team]["units"].values()
                start_time = time.time()

                for unit in units:
                    if unit.canAct():
                        if is_opponent:
                            # Call the opponent directly for unit decision
                            action = self.agents[team].decide_action(unit.id, None, unit.team, newTurn)
                            if action is not None:
                                self.actionBuffer.append( action )
                        elif self.agents[team] == None:
                            # RL training agent that is controlling the simulation
                            # The enviornment then handles this unit, and calls take_action() to buffer a requested action
                            yield (unit.id, None, unit.team, newTurn)
                        else:
                            raise Exception("Invalid agent type. Should be None for the training agent or inherit from 'AgentOpponent' for an opponent.")
                        newTurn = False
                
                cities = self.game.cities.values()
                for city in cities:
                    if city.team == team:
                        for cell in city.citycells:
                            citytile = cell.citytile
                            if citytile.canAct():
                                if is_opponent:
                                    # Call the opponent directly for unit decision
                                    self.actionBuffer.append( self.agents[team].decide_action(None, citytile.cityid, citytile.team, newTurn) )
                                    if action is not None:
                                        self.actionBuffer.append( action )
                                elif self.agents[team] == None:
                                    # RL training agent that is controlling the simulation
                                    # The enviornment then handles this city, and calls take_action() to buffer a requested action
                                    yield (None, citytile.cityid, citytile.team, newTurn)
                                else:
                                    raise Exception("Invalid agent type. Should be None for the training agent or inherit from 'AgentOpponent' for an opponent.")
                                newTurn = False
                
                actionsTimeTaken[team] = time.time() - start_time
            
            #print("Time taken per agent for turn: (%.3fs, %.3fs)", actionsTimeTaken[0], actionsTimeTaken[1])
            
            # Now let the game actually process the requested actions and play the turn
            game_over = self.game.runTurnWithActions(self.actionBuffer)
            self.actionBuffer = []

