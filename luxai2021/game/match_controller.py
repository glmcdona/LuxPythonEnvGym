import random
import sys
import time
import traceback

from .constants import Constants
from ..env.agent import Agent


class GameStepFailedException(Exception):
    pass


class MatchController:
    def __init__(self, game, agents=[None, None]) -> None:
        """

        :param game:
        :param agents:
        """
        self.action_buffer = []
        self.game = game
        self.agents = agents

        if len(agents) != 2:
            raise ValueError("Two agents must be specified.")

        # Validate the agents
        self.training_agent_count = 0
        for i, agent in enumerate(agents):
            if not (issubclass(type(agent), Agent) or isinstance(agent, Agent)):
                raise ValueError("All agents must inherit from Agent.")
            if agent.get_agent_type == Constants.AGENT_TYPE.LEARNING:
                self.training_agent_count += 1

            # Initialize agent
            agent.set_team(i)
            agent.set_controller(self)

        if self.training_agent_count > 1:
            raise ValueError("At most one agent must be trainable.")

        elif self.training_agent_count == 1:
            print("Running in training mode.", file=sys.stderr)

        elif self.training_agent_count == 0:
            print("Running in inference-only mode.", file=sys.stderr)

    def reset(self):
        """

        :return:
        """
        # Randomly re-assign teams of the agents
        r = random.randint(0, 1)
        self.agents[0].set_team(r)
        self.agents[1].set_team((r + 1) % 2)

        # Reset the game
        self.game.reset()
        self.action_buffer = []

    def take_action(self, action):
        """
         Adds the specified action to the action buffer
         """
        if action is not None:
            # Validate the action
            if action.is_valid(self.game):
                # Add the action
                self.action_buffer.append(action)

    def take_actions(self, actions):
        """
         Adds the specified action to the action buffer
         """
        for action in actions:
            self.take_action(action)

    def log_error(self, text):
        # Ignore errors caused by logger
        try:
            if text is not None:
                with open("match_errors.txt", "a") as o:
                    o.write(text + "\n")
        except Exception:
            print("Critical error in logging")

    def set_opponent_team(self, agent, team):
        """
        Sets the team of the opposing team
        """
        for a in self.agents:
            if a != agent:
                a.set_team(team)

    def run_to_next_observation(self):
        """ 
            Generator function that gets the observation at the next Unit/City
            to be controlled.
            Returns: tuple describing the unit who's control decision is for (unit_id, city, team, is new turn)
        """
        game_over = False
        while not game_over:
            # Run pre-turn agent events to allow for them to handle running the turn instead (used in a kaggle submission agent)
            for agent in self.agents:
                agent.pre_turn(self.game)

            # Process this turn
            for agent in self.agents:
                if agent.get_agent_type() == Constants.AGENT_TYPE.AGENT:
                    # Call the agent for the set of actions
                    actions = agent.process_turn(self.game, agent.team)
                    self.take_actions(actions)
                elif agent.get_agent_type() == Constants.AGENT_TYPE.LEARNING:
                    # Yield the game to make a decision, since the learning environment is the function caller
                    new_turn = True
                    start_time = time.time()

                    units = self.game.state["teamStates"][agent.team]["units"].values()
                    for unit in units:
                        if unit.can_act():
                            # RL training agent that is controlling the simulation
                            # The enviornment then handles this unit, and calls take_action() to buffer a requested action
                            yield unit, None, unit.team, new_turn
                            new_turn = False

                    cities = self.game.cities.values()
                    for city in cities:
                        if city.team == agent.team:
                            for cell in city.city_cells:
                                city_tile = cell.city_tile
                                if city_tile.can_act():
                                    # RL training agent that is controlling the simulation
                                    # The enviornment then handles this city, and calls take_action() to buffer a requested action
                                    yield None, city_tile, city_tile.team, new_turn
                                    new_turn = False

                    time_taken = time.time() - start_time

            # Now let the game actually process the requested actions and play the turn
            try:
                # Run post-turn agent events to allow for them to handle running the turn instead (used in a kaggle submission agent)
                handled = False
                for agent in self.agents:
                    if agent.post_turn(self.game, self.action_buffer):
                        handled = True

                if not handled:
                    game_over = self.game.run_turn_with_actions(self.action_buffer)
            except Exception as e:
                # Log exception
                self.log_error("ERROR: Critical error occurred in turn simulation.")
                self.log_error(repr(e))
                self.log_error(''.join(traceback.format_exception(None, e, e.__traceback__)))
                raise GameStepFailedException("Critical error occurred in turn simulation.")

            self.action_buffer = []
