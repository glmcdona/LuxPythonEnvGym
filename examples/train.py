import gym
import json
import datetime as dt

from stable_baselines3 import PPO # pip install stable-baselines3
from luxai2021.env.lux_env import LuxEnvironment
from luxai2021.game.constants import LuxMatchConfigs_Default
from luxai2021.game.match_controller import AgentOpponent

configs = LuxMatchConfigs_Default
opponent = AgentOpponent()
env = LuxEnvironment(configs, opponent)
model = PPO("MlpPolicy", env, verbose=1)

model.learn(total_timesteps=20000)

obs = env.reset()
for i in range(2000):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
    if done:
      print("Episode done, resetting.")
      obs = env.reset()

env.close()
