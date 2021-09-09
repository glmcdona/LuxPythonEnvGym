"""
Implements /src/Actionable/index.ts
"""


class Actionable:
    """
    Enum implementation
    """

    class Types:
        WOOD = 'wood'
        COAL = 'coal'
        URANIUM = 'uranium'

    def __init__(self, configs, cooldown=0.0) -> None:
        """

        :param configs:
        :param cooldown:
        """
        self.configs = configs
        self.current_actions = []
        self.cooldown = cooldown

    def can_act(self) -> bool:
        """

        :return:
        """
        return self.cooldown < 1

    def handle_turn(self, game):
        """

        :param game:
        :return:
        """
        try:
            # ToDo self.turn() is not implemented
            self.turn(game)
        finally:
            self.current_actions = []
        # reset actions to empty

    def give_action(self, action):
        """

        :param action:
        :return:
        """
        self.current_actions.append(action)
