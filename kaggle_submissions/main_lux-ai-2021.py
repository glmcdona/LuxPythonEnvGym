from stable_baselines3 import PPO  # pip install stable-baselines3

from luxai2021.env.agent import AgentFromStdInOut
from luxai2021.env.lux_env import LuxEnvironment
from luxai2021.game.constants import LuxMatchConfigs_Default
from agent_policy import AgentPolicy

if __name__ == "__main__":
    """
    This is a kaggle submission, so we don't use command-line args
    and assume the model is in model.zip in the current folder.
    """
    # Tool to run this against itself locally:
    # "lux-ai-2021 --seed=100 main_lux-ai-2021.py main_lux-ai-2021.py --maxtime 10000"

    # Run a kaggle submission with the specified model
    configs = LuxMatchConfigs_Default

    # Load the saved model
    #model_id = 5403
    #total_steps = int(48e6)
    #model = PPO.load(f"models/rl_model_{model_id}_{total_steps}_steps.zip")
    model = PPO.load(f"model.zip")
    
    # Create a kaggle-remote opponent agent
    opponent = AgentFromStdInOut()

    # Create a RL agent in inference mode
    player = AgentPolicy(mode="inference", model=model)

    # Run the environment
    env = LuxEnvironment(configs, player, opponent)
    env.reset()  # This will automatically run the game since there is
    # no controlling learning agent.
