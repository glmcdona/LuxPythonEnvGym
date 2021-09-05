
'''Implements /src/Actionable/index.ts'''

class Actionable:
    ''' Enum implemenation '''
    class Types:
        WOOD = 'wood'
        COAL = 'coal'
        URANIUM = 'uranium'

    def __init__(self, configs, cooldown = 0.0) -> None:
        self.configs = configs
        self.currentActions = []
        self.cooldown = cooldown
    
    def canAct(self) -> bool:
        return self.cooldown < 1
    
    def handleTurn(self, game):
        try:
            self.turn(game)
        finally:
            self.currentActions = []
        # reset actions to empty

    def giveAction(self, action):
        self.currentActions.append(action)
