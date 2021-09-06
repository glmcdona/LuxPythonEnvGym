from ..game.constants import Constants

''' Implements the base class for a training Agent '''
class Agent():
    def __init__(self) -> None:
        """
        Implements an agent opponent
        """
        self.team = None
    
    def processTurn(self, game, team):
        """
        Decides on a set of actions for the current turn.
        Returns: Array of actions to perform for this turn.
        """
        return []

    def preTurn(self, game):
        """
        Called before a turn starts. Allows for modifying the game environment.
        Generally only used in kaggle submission opponents.
        """
        return
    
    def postTurn(self, game, actions):
        """
        Called after a turn. Generally only used in kaggle submission opponents.
            Returns True if it handled the turn (don't run our game engine)
        """
        return False

    def getAgentType(self):
        """
        Returns the type of agent. Use AGENT for inference, and LEARNING for training a model.
        """
        return Constants.AGENT_TYPE.AGENT
    
    def setTeam(self, team):
        """
        Sets the team id that this agent is controlling
        """
        self.team = team
    
    def setController(self, matchController):
        self.matchController = matchController



"""
Wrapper for an external agent where this agent's commands are coming in through standard input.
"""
class AgentFromStdInOut(Agent):
    def __init__(self) -> None:
        """
        Implements an agent opponent
        """
        self.team = None
        self.initializedPlayer = False
        self.initializedMap = False
    
    def preTurn(self, game):
        """
        Called before a turn starts. Allows for modifying the game environment.
        Generally only used in kaggle submission opponents.
        """
        
        # Read StdIn to update game state
        # Loosly implements:
        #    /Lux-AI-Challenge/Lux-Design-2021/blob/master/kits/python/simple/main.py
        #    AND /kits/python/simple/agent.py agent(observation, configuration)
        updates = []
        while True:
            message = input()

            if self.initializedPlayer == False:
                team = int(message)
                self.setTeam((team+1)%2)
                self.matchController.setOpponentTeam(self, team)
                
                self.initializedPlayer = True
            
            elif self.initializedMap == False:
                # Parse the map size update message, it's always the second message of the game
                mapInfo = message.split(" ")
                game.configs["width"] = int(mapInfo[0])
                game.configs["height"] = int(mapInfo[1])

                # Use an empty map, because the updates will fill the map out
                game.configs["mapType"] = Constants.MAP_TYPES.EMPTY 

                self.initializedMap = True
            else:
                updates.append(message)
            
            if message == "D_DONE": # End of turn data marker
                break

        # Reset the game to the specified state
        game.reset(updates = updates)

    def postTurn(self, game, actions):
        """
        Called after a turn. Generally only used in kaggle submission opponents.
            Returns True if it handled the turn (don't run our game engine)
        """
        # TODO: Send the list of actions to stdout in the correct format.
        messages = []
        for action in actions:
            messages.append(action.toMessage(game))
        
        # Print the messages to the kaggle controller
        if len(messages) > 0:
            print(",".join(messages))
        print("D_FINISH")
        
        # True here instructs the controller to not simulate the actions. Instead the kaggle controller will
        # run the turn and send back pre-turn map state.
        return True