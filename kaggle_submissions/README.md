# Preparing a kaggle submission

You have trained a model, and now you'd like to submit it as a kaggle submission. Here are the steps to prepare your submission.

Either view this Kaggle Notebook example:
* TBD

Or prepare a submission yourself
1. Copy your model into this folder as "model.zip"
1. Copy your `agent_policy.py` logic into this folder
1. Copy two required python package dependencies into this folder (luxai2021 and stable_baselines3). To do this run `python download_dependencies.py` in this folder or copy them manually yourself
1. Tarball this current folder into a submission `tar -czf ./../submission.tar.gz *`
