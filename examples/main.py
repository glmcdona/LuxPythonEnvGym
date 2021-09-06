from luxai2021.game.constants import LuxMatchConfigs_Default
from stable_baselines3 import PPO # pip install stable-baselines3
from luxai2021.env.lux_env import LuxEnvironment
from luxai2021.env.agent import Agent, AgentFromStdInOut
from train import AgentPolicy

if __name__ == "__main__":
    """
    This is a kaggle submission, so we don't use command-line args
    and assume the model is in model.zip in the current folder.
    """
    # Tool to run this against itself locally:
    # "lux-ai-2021 --seed=100 main.py main.py --maxtime 10000"

    # Run a kaggle submission with the specified model
    configs = LuxMatchConfigs_Default

    # Load the saved model
    model = PPO.load("model.zip")
    
    # Create a kaggle-remote opponent agent
    opponent = AgentFromStdInOut()

    # Create a RL agent in inference mode
    player = AgentPolicy(mode="inference", model=model)
    
    # Run the environment
    env = LuxEnvironment(configs, player, opponent)
    env.reset() # This will automatically run the game since there is
                # no controlling learning agent.
