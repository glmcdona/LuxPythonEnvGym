"""
Implements /src/Actions/index.ts
"""
from .constants import Constants

UNIT_TYPES = Constants.UNIT_TYPES


class Action:
    def __init__(self, action, team):
        self.action = action
        self.team = team

    def is_valid(self, game):
        """
        Validates the command.
        :param game:
        :return: True if it's valid, False otherwise
        """
        return True

    def to_message(self, game):
        """
        Converts this action into a text message to send the kaggle controller via StdOut
        :param game:
        :return: String-serialized action message to send kaggle controller
        """
        raise Exception("NOT IMPLEMENTED")


class MoveAction(Action):
    def __init__(self, team, unit_id, direction, **kwarg):
        """

        :param team:
        :param unit_id:
        :param direction:
        :param kwarg:
        """
        action = Constants.ACTIONS.MOVE
        self.unit_id = unit_id
        self.direction = direction
        super().__init__(action, team)

    def is_valid(self, game) -> bool:
        """
        Validates the command.
        :param game:
        :return: (bool) True if it's valid, False otherwise
        """
        if self.unit_id is None or self.team is None or self.direction is None:
            return False

        unit = game.get_unit(self.team, self.unit_id)

        # Validate it can act
        if not unit.can_act():
            return False

        # Check map bounds of destination spot
        new_pos = unit.pos.translate(self.direction, 1)
        if new_pos.y < 0 or new_pos.y >= game.map.height:
            return False
        if new_pos.x < 0 or new_pos.x >= game.map.height:
            return False

        # Note: Collisions are handled in the turn loop as both players move
        return True

    def to_message(self, game) -> str:
        """
        Converts this action into a text message to send the kaggle controller via StdOut
        :param game:
        :return: (str) String-serialized action message to send kaggle controller
        """
        return "m {} {}".format(self.unit_id, self.direction)


class SpawnAction(Action):
    def __init__(self, action, team, unit_id, x, y, **kwarg):
        """
        
        :param action: 
        :param team: 
        :param unit_id: 
        :param x: 
        :param y: 
        :param kwarg: 
        """
        self.unit_id = unit_id
        self.x = x
        self.y = y
        super().__init__(action, team)


class SpawnCartAction(SpawnAction):
    def __init__(self, team, unit_id, x, y, **kwarg):
        """
        
        :param team: 
        :param unit_id: 
        :param x: 
        :param y: 
        :param kwarg: 
        """
        action = Constants.ACTIONS.BUILD_CART
        self.type = UNIT_TYPES.CART
        super().__init__(action, team, unit_id, x, y)

    def is_valid(self, game):
        """
        Validates the command.
        ::param game:
        :return: True if it's valid, False otherwise
        """
        if self.x is None or self.y is None or self.team is None:
            return False

        city_tile = game.map.get_cell(self.x, self.y).city_tile
        if city_tile is None:
            return False

        if not city_tile.can_build_unit():
            return False

        # TODO handle multiple units building workers in same turn
        if game.cart_unit_cap_reached(self.team):
            return False

        return True

    def to_message(self, game) -> str:
        """
        Converts this action into a text message to send the kaggle controller via StdOut
        :param game: 
        :return: (str) String-serialized action message to send kaggle controller
        """
        return "bc {} {}".format(self.x, self.y)


class SpawnWorkerAction(SpawnAction):
    def __init__(self, team, unit_id, x, y, **kwarg):
        """
        
        :param team: 
        :param unit_id: 
        :param x: 
        :param y: 
        :param kwarg: 
        """
        action = Constants.ACTIONS.BUILD_WORKER
        self.type = UNIT_TYPES.WORKER
        super().__init__(action, team, unit_id, x, y)

    def is_valid(self, game):
        """
        Validates the command.
        :param game:
        :return: (bool) True if it's valid, False otherwise
        """
        if self.x is None or self.y is None or self.team is None:
            return False

        if self.y < 0 or self.y >= game.map.height:
            return False
        if self.x < 0 or self.x >= game.map.height:
            return False

        city_tile = game.map.get_cell(self.x, self.y).city_tile
        if city_tile is None:
            return False

        if not city_tile.can_build_unit():
            return False

        # TODO handle multiple units building workers in same turn
        if game.worker_unit_cap_reached(self.team):
            return False

        return True

    def to_message(self, game) -> str:
        """
        Converts this action into a text message to send the kaggle controller via StdOut
        :param game:
        :return: (str) String-serialized action message to send kaggle controller
        """
        return "bw {} {}".format(self.x, self.y)


class SpawnCityAction(Action):
    def __init__(self, team, unit_id, **kwarg):
        """

        :param team:
        :param unit_id:
        :param kwarg:
        """
        action = Constants.ACTIONS.BUILD_CITY
        self.unit_id = unit_id
        super().__init__(action, team)

    def is_valid(self, game) -> bool:
        """
        Validates the command.
        :param game:
        :return: (bool) True if it's valid, False otherwise
        """
        if self.unit_id is None or self.team is None:
            return False

        unit = game.get_unit(self.team, self.unit_id)

        # Validate it can act
        if not unit.can_act():
            return False

        if not unit.can_build(game.map):
            return False

        # Validate the cell
        cell = game.map.get_cell_by_pos(unit.pos)
        if cell.is_city_tile():
            return False

        if cell.has_resource():
            return False

        # Note: Collisions are handled in the turn loop as both players move
        return True

    def to_message(self, game) -> str:
        """
        Converts this action into a text message to send the kaggle controller via StdOut
        :param game:
        :return: (str) String-serialized action message to send kaggle controller
        """
        return "bcity {}".format(self.unit_id)


class TransferAction(Action):
    def __init__(self, team, source_id, destination_id, resource_type, amount):
        """

        :param team:
        :param source_id:
        :param destination_id:
        :param resource_type:
        :param amount:
        """
        action = Constants.ACTIONS.TRANSFER
        self.source_id = source_id
        self.destination_id = destination_id
        self.resource_type = resource_type
        self.amount = amount
        super().__init__(action, team)

    def to_message(self, game):
        """
        Converts this action into a text message to send the
        kaggle controller via StdOut
        Returns: String-serialized action message to send kaggle controller
        """
        return "t {} {} {} {}".format(self.source_id, self.destination_id, self.resource_type, self.amount)


class PillageAction(Action):
    def __init__(self, team, unit_id):
        """
        
        :param team: 
        :param unit_id: 
        """
        action = Constants.ACTIONS.PILLAGE
        self.unit_id = unit_id
        super().__init__(action, team)

    def to_message(self, game) -> str:
        """
        Converts this action into a text message to send the kaggle controller via StdOut
        :param game:
        :return: (str) String-serialized action message to send kaggle controller
        """
        return "p {}".format(self.unit_id)


class ResearchAction(Action):
    def __init__(self, team, x, y):
        action = Constants.ACTIONS.RESEARCH
        self.x = x
        self.y = y
        super().__init__(action, team)

    def to_message(self, game) -> str:
        """
        Converts this action into a text message to send the kaggle controller via StdOut
        :param game:
        :return: (str) String-serialized action message to send kaggle controller
        """
        return "r {} {}".format(self.x, self.y)
