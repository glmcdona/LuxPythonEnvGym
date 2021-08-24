
'''Implements /src/Actionable/index.ts'''

class Actionable:
    ''' Enum implemenation '''
    class Types:
        WOOD = 'wood'
        COAL = 'coal'
        URANIUM = 'uranium'

    def __init__(self, configs) -> None:
        self.configs = configs
        self.currentActions = []
        self.cooldown = 0.0
    
    def can_act(self) -> bool:
        return self.cooldown < 1
    
    def handle_turn(self, game):
        try:
            self.turn(game)
        finally:
            self.currentActions = []
        # reset actions to empty

    def give_action(self, action):
        self.currentActions.append(action)
