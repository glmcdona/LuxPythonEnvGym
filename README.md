# LuxPythonEnvGym
Matching python environment code for Lux AI 2021 Kaggle competition, and a gym interface for RL models.

This is still in-progress and not ready for use yet. I'll post official docs and usage guide here once a simple example converges, and can be transformed to a kaggle-submission format.


| **Features**                         | **LuxAi2021** |
| ------------------------------------ | ----------------------|
| Lux game engine porting to python    | :heavy_check_mark: |
| Documentation                        | :x: |
| All actions supported                | :x: |
| PPO example training agent           | :heavy_check_mark:  |
| Example agent converges to a good policy | :heavy_check_mark: |
| Kaggle submission format agents      | :x: |
| Lux replay viewer support            | :x: |
| Game engine consistency validation to base game       | :x: |

## Installation
See above, this project isn't complete yet. If you want to try your own agents anyways, here are instructions. This should work cross-platform, but I've only tested Windows 10 and Ubuntu.

Install luxai2021 environment package by running the installer:

```python setup.py install```

Now edit and run your ML agent training code:

```python ./examples/train.py```

You can then run tensorboard to monitor the training:

```tensorboard --logdir lux_tensorboard```

## Kaggle submissions of your agent
Place your trained model as "model.zip" in the same folder as ./examples/main.py.

Assuming you have the lux-ai-2021 tools installed, you can then run a kaggle match and generate replays locally, eg:
```lux-ai-2021 --seed=100 main.py main.py --maxtime 10000```

TBD: Working on creating the format of the submission.zip that installs dependencies correctly.
