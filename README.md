# LuxPythonEnvGym
This is a replica of the Lux AI 2021 game ported directly over to python. It also sets up a classic Reinforcement Learning gym environment to be used to train RL agents for creating agents.


| **Features**                         | **LuxAi2021** |
| ------------------------------------ | ----------------------|
| Lux game engine porting to python    | :heavy_check_mark: |
| Documentation                        | :x: |
| All actions supported                | :heavy_check_mark: |
| PPO example training agent           | :heavy_check_mark:  |
| Example agent converges to a good policy | :heavy_check_mark: |
| Kaggle submission format agents      | :heavy_check_mark: |
| Lux replay viewer support            | :heavy_check_mark: |
| Game engine consistency validation to base game       | :x: |

## Installation
This should work cross-platform, but I've only tested Windows 10 and Ubuntu.

**Important:** Use Python 3.7.* for training your models. This is required since when you create a Kaggle submission, the Kaggle competition will run the code using Python 3.7.*, and you will get a model deserialization error if you train the model with Python 3.8>=.

Install luxai2021 environment package by running the installer:

```python setup.py install```


## Example python ML training
Create your own agent logic, observations, actions, and rewards by modifying this example:

https://github.com/glmcdona/LuxPythonEnvGym/blob/main/examples/agent_policy.py

Then train your model by:

```python ./examples/train.py```

You can then run tensorboard to monitor the training:

```tensorboard --logdir lux_tensorboard```


## Example kaggle notebook
Here is a complete training, inference, and kaggle submission example in Notebook format:

https://www.kaggle.com/glmcdona/lux-ai-deep-reinforcement-learning-ppo-example


## Preparing a kaggle submission

You have trained a model, and now you'd like to submit it as a kaggle submission. Here are the steps to prepare your submission.

Either view the above kaggle example or prepare a submission yourself:
1. Place your trained model file as `model.zip` and your agent file `agent_policy.py` in the `./kaggle_submissions/` folder.
1. Run `python download_dependencies.py` in `./kaggle_submissions/` to copy two required python package dependencies into this folder (luxai2021 and stable_baselines3).
1. Tarball the folder into a submission `tar -czf submission.tar.gz -C kaggle_submissions .`

**Important:** The model.zip needs to have been trained on Python 3.7.* or you get a deserialization error, since this is the python version that Kaggle Environment uses to inference the model in submission.

## Creating and viewing a replay
Place your trained model file as `model.zip` and your agent file `agent_policy.py` in the `./kaggle_submissions/` folder. Then run a command like the following from that directory:

`lux-ai-2021 --seed=100 ./kaggle_submissions/main_lux-ai-2021.py ./kaggle_submissions/main_lux-ai-2021.py --maxtime 10000`

This will battle your agent against itself and produce a replay match. You can view the replay here:
https://2021vis.lux-ai.org/
