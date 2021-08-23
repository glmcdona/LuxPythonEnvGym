import gym
import json
import datetime as dt

from stable_baselines3 import PPO # pip install stable-baselines3

from env.lux_env import LuxPerUnitEnvironment

env = LuxPerUnitEnvironment(map_height=30, map_width=30)
model = PPO("MlpPolicy", env, verbose=1)

model.learn(total_timesteps=20000)

obs = env.reset()
for i in range(2000):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
    if done:
      obs = env.reset()

env.close()
