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