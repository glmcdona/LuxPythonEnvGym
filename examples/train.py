import argparse
import glob
import os
import random
from typing import Callable

from stable_baselines3 import PPO  # pip install stable-baselines3
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.utils import set_random_seed, get_schedule_fn
from stable_baselines3.common.vec_env import SubprocVecEnv

from .agent_policy import AgentPolicy
from luxai2021.env.agent import Agent
from luxai2021.env.lux_env import LuxEnvironment
from luxai2021.game.constants import LuxMatchConfigs_Default


# https://stable-baselines3.readthedocs.io/en/master/guide/examples.html?highlight=SubprocVecEnv#multiprocessing-unleashing-the-power-of-vectorized-environments
def make_env(local_env, rank, seed=0):
    """
    Utility function for multi-processed env.

    :param local_env: (LuxEnvironment) the environment 
    :param seed: (int) the initial seed for RNG
    :param rank: (int) index of the subprocess
    """

    def _init():
        local_env.seed(seed + rank)
        return local_env

    set_random_seed(seed)
    return _init


def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    Linear learning rate schedule.

    :param initial_value: (float) Initial learning rate.
    :return: schedule that computes current learning rate depending on remaining progress
    """

    def func(progress_remaining: float) -> float:
        """
        Progress will decrease from 1 (beginning) to 0.

        :param progress_remaining: (float)
        :return: (float) current learning rate
        """
        return progress_remaining * initial_value

    return func


def get_command_line_arguments():
    """
    Get the command line arguments
    :return:(ArgumentParser) The command line arguments as an ArgumentParser
    """
    parser = argparse.ArgumentParser(description='Training script for Lux RL agent.')
    parser.add_argument('--id', help='Identifier of this run', type=str, default=str(random.randint(0, 10000)))
    parser.add_argument('--learning_rate', help='Learning rate', type=float, default=0.001)
    parser.add_argument('--gamma', help='Gamma', type=float, default=0.995)
    parser.add_argument('--gae_lambda', help='GAE Lambda', type=float, default=0.95)
    parser.add_argument('--batch_size', help='batch_size', type=int, default=2048)  # 64
    parser.add_argument('--step_count', help='Total number of steps to train', type=int, default=10000000)
    parser.add_argument('--n_steps', help='Number of experiences to gather before each learning period', type=int, default=2048*8)
    parser.add_argument('--path', help='Path to a checkpoint to load to resume training', type=str, default=None)
    args = parser.parse_args()

    return args


def train(args):
    """
    The main training loop
    :param args: (ArgumentParser) The command line arguments
    """
    print(args)

    # Run a training job
    configs = LuxMatchConfigs_Default

    # Create a default opponent agent
    opponent = Agent()

    # Create a RL agent in training mode
    player = AgentPolicy(mode="train")

    # Train the model
    num_cpu = 1
    if num_cpu == 1:
        env = LuxEnvironment(configs=configs,
                             learning_agent=player,
                             opponent_agent=opponent)
    else:
        env = SubprocVecEnv([make_env(LuxEnvironment(configs=configs,
                                                     learning_agent=AgentPolicy(mode="train"),
                                                     opponent_agent=opponent), i) for i in range(num_cpu)])
    run_id = args.id
    print("Run id %s" % run_id)

    if args.path:
        # by default previous model params are used (lr, batch size, gamma...)
        model = PPO.load(args.path)
        model.set_env(env=env)

        # Update the learning rate
        model.lr_schedule = get_schedule_fn(args.learning_rate)

        # TODO: Update other training parameters
    else:
        model = PPO("MlpPolicy",
                    env,
                    verbose=1,
                    tensorboard_log="./lux_tensorboard/",
                    learning_rate=args.learning_rate,
                    gamma=args.gamma,
                    gae_lambda=args.gae_lambda,
                    batch_size=args.batch_size,
                    n_steps=args.n_steps
                    )

    print("Training model...")
    # Save a checkpoint every 1M steps
    checkpoint_callback = CheckpointCallback(save_freq=1000000,
                                             save_path='./models/',
                                             name_prefix=f'rl_model_{run_id}')
    model.learn(total_timesteps=args.step_count,
                callback=checkpoint_callback)  # 20M steps
    if not os.path.exists(f'models/rl_model_{run_id}_{args.step_count}_steps.zip'):
        model.save(path=f'models/rl_model_{run_id}_{args.step_count}_steps.zip')
    print("Done training model.")

    # Inference the model
    print("Inference model policy with rendering...")
    saves = glob.glob(f'models/rl_model_{run_id}_*_steps.zip')
    latest_save = sorted(saves, key=lambda x: int(x.split('_')[-2]), reverse=True)[0]
    model.load(path=latest_save)
    obs = env.reset()
    for i in range(600):
        action_code, _states = model.predict(obs, deterministic=True)
        obs, rewards, done, info = env.step(action_code)
        if i % 5 == 0:
            print("Turn %i" % i)
            env.render()

        if done:
            print("Episode done, resetting.")
            obs = env.reset()
    print("Done")

    '''
    # Learn with self-play against the learned model as an opponent now
    print("Training model with self-play against last version of model...")
    player = AgentPolicy(mode="train")
    opponent = AgentPolicy(mode="inference", model=model)
    env = LuxEnvironment(configs, player, opponent)
    model = PPO("MlpPolicy",
        env,
        verbose=1,
        tensorboard_log="./lux_tensorboard/",
        learning_rate = 0.0003,
        gamma=0.999,
        gae_lambda = 0.95
    )

    model.learn(total_timesteps=2000)
    env.close()
    print("Done")
    '''


if __name__ == "__main__":
    # Get the command line arguments
    local_args = get_command_line_arguments()

    # Train the model
    train(local_args)
