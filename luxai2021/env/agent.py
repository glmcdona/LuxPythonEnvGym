from ..game.constants import Constants

"""
Implements the base class for a training Agent
"""


class Agent:
    def __init__(self, replay=None) -> None:
        """
        Implements an agent opponent
        """
        self.replay = replay
        self.team = None
        self.match_controller = None
        self.action_space = None
        self.observation_space = None
    
    def game_start(self, game):
        """
        This funciton is called at the start of each game. Use this to
        reset and initialize per game. Note that self.team may have
        been changed since last game. The game map has been created
        and starting units placed.

        Args:
            game ([type]): Game.
        """
        pass

    def process_turn(self, game, team):
        """
        Decides on a set of actions for the current turn.
        :param game:
        :param team:
        :return: Array of actions to perform for this turn.
        """
        actions = []
        turn = game.state["turn"]

        if self.replay is not None:
            acts = self.replay['steps'][turn+1][team]["action"]
            acts = [game.action_from_string(a, team) for a in acts]
            acts = [a for a in acts if a is not None]
            actions.extend(acts)
        
        return actions

    def pre_turn(self, game, is_first_turn=False):
        """
        Called before a turn starts. Allows for modifying the game environment.
        Generally only used in kaggle submission opponents.
        :param game:
        """
        return

    def post_turn(self, game, actions):
        """
        Called after a turn. Generally only used in kaggle submission opponents.
        :param game:
        :param actions:
        :return: (bool) True if it handled the turn (don't run our game engine)
        """
        return False

    def get_agent_type(self):
        """
        Returns the type of agent. Use AGENT for inference, and LEARNING for training a model.
        """
        return Constants.AGENT_TYPE.AGENT

    def set_team(self, team):
        """
        Sets the team id that this agent is controlling
        :param team:
        """
        self.team = team

    def set_controller(self, match_controller):
        """

        """
        self.match_controller = match_controller


"""
Wrapper for an external agent where this agent's commands are coming in through standard input.
"""


class AgentFromStdInOut(Agent):
    def __init__(self) -> None:
        """
        Implements an agent opponent
        """
        super().__init__()
        self.initialized_player = False
        self.initialized_map = False

    def pre_turn(self, game, is_first_turn=False):
        """
        Called before a turn starts. Allows for modifying the game environment.
        Generally only used in kaggle submission opponents.
        :param game:
        """

        # Read StdIn to update game state
        # Loosly implements:
        #    /Lux-AI-Challenge/Lux-Design-2021/blob/master/kits/python/simple/main.py
        #    AND /kits/python/simple/agent.py agent(observation, configuration)
        updates = []
        while True:
            message = input()

            if not self.initialized_player:
                team = int(message)
                self.set_team((team + 1) % 2)
                self.match_controller.set_opponent_team(self, team)

                self.initialized_player = True

            elif not self.initialized_map:
                # Parse the map size update message, it's always the second message of the game
                map_info = message.split(" ")
                game.configs["width"] = int(map_info[0])
                game.configs["height"] = int(map_info[1])

                # Use an empty map, because the updates will fill the map out
                game.configs["mapType"] = Constants.MAP_TYPES.EMPTY

                self.initialized_map = True
            else:
                updates.append(message)

            if message == "D_DONE":  # End of turn data marker
                break
        
        # Reset the game to the specified state. Don't increment turn counter on first turn of game.
        game.reset(updates=updates, increment_turn=not is_first_turn)

    def post_turn(self, game, actions) -> bool:
        """
        Called after a turn. Generally only used in kaggle submission opponents.
        :param game:
        :param actions:
        :return: (bool) True if it handled the turn (don't run our game engine)
        """
        # TODO: Send the list of actions to stdout in the correct format.
        messages = []
        for action in actions:
            messages.append(action.to_message(game))

        # Print the messages to the kaggle controller
        if len(messages) > 0:
            print(",".join(messages))
        else:
            # Print a new line. This is needed for the main_kaggle_submission.py wrapper to work
            print("")

        print("D_FINISH")

        # True here instructs the controller to not simulate the actions. Instead the kaggle controller will
        # run the turn and send back pre-turn map state.
        return True
