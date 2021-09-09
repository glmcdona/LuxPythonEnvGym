"""
Implements the base class for a Lux environment
"""
import gym

from ..game.game import Game
from ..game.match_controller import GameStepFailedException, MatchController


class LuxEnvironment(gym.Env):
    """
    Custom Environment that follows gym interface
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, configs, learning_agent, opponent_agent):
        """
        THe initializer
        :param configs:
        :param learning_agent:
        :param opponent_agent:
        """
        super(LuxEnvironment, self).__init__()

        # Create the game
        self.game = Game(configs)
        self.match_controller = MatchController(self.game, agents=[learning_agent, opponent_agent])

        self.action_space = learning_agent.action_space
        self.observation_space = learning_agent.observation_space

        self.learning_agent = learning_agent

        self.current_step = 0
        self.match_generator = None

        self.last_observation_object = None

    def step(self, action_code):
        """
        Take this action, then get the state at the next action
        :param action_code:
        :return:
        """
        # Decision for 1 unit or city
        self.learning_agent.take_action(action_code,
                                        self.game,
                                        unit=self.last_observation_object[0],
                                        city_tile=self.last_observation_object[1],
                                        team=self.last_observation_object[2]
                                        )

        self.current_step += 1

        # Get the next observation
        is_new_turn = True
        is_game_over = False
        is_game_error = False
        try:
            (unit, city_tile, team, is_new_turn) = next(self.match_generator)

            obs = self.learning_agent.get_observation(self.game, unit, city_tile, team, is_new_turn)
            self.last_observation_object = (unit, city_tile, team, is_new_turn)
        except StopIteration:
            # The game episode is done.
            is_game_over = True
            obs = None
        except GameStepFailedException:
            # Game step failed, assign a game lost reward to not incentivise this
            is_game_over = True
            obs = None
            is_game_error = True

        # Calculate reward for this step
        reward = self.learning_agent.get_reward(self.game, is_game_over, is_new_turn, is_game_error)

        return obs, reward, is_game_over, {}

    def reset(self):
        """

        :return:
        """
        self.current_step = 0
        self.last_observation_object = None

        # Reset game + map
        self.match_controller.reset()
        self.match_generator = self.match_controller.run_to_next_observation()
        (unit, city_tile, team, is_new_turn) = next(self.match_generator)

        obs = self.learning_agent.get_observation(self.game, unit, city_tile, team, is_new_turn)
        self.last_observation_object = (unit, city_tile, team, is_new_turn)

        return obs

    def render(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        print(self.current_step)
        print(self.game.map.get_map_string())
