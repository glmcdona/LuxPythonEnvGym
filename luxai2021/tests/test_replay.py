import pytest
import json
from luxai2021.game.constants import LuxMatchConfigs_Default
from luxai2021.env.lux_env import LuxEnvironment
from luxai2021.env.agent import Agent

@pytest.mark.parametrize("replay_id",['27095556', 
                                      '26835897', 
                                      '26773935', 
                                      '26691974', 
                                      '26688997', 
                                      '26690562', 
                                      '27075871'])
def test_run_replay(replay_id):
    print("Testing simulated replays...")
    print(replay_id)

    with open(f"C:/StudioProjects/Lux/replays/episodes/{replay_id}.json", mode="r") as replay_file:
        json_args = json.load(replay_file)
    
    config = LuxMatchConfigs_Default.copy()
    config['seed'] = json_args['configuration']['seed']

    opponent = Agent(replay=json_args)
    agent = Agent(replay=json_args)

    env = LuxEnvironment(configs=config,
                        learning_agent=agent,
                        opponent_agent=opponent,
                        replay_validate=json_args)

    is_game_error = env.run_no_learn()
    assert not is_game_error

    return True
