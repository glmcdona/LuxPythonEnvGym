
'''Implements /src/Resource/index.ts'''

class Resource:
    ''' Enum implemenation '''
    class Types:
        WOOD = 'wood'
        COAL = 'coal'
        URANIUM = 'uranium'

    def __init__(self, type, amount) -> None:
        self.type = type
        self.amount = amount

