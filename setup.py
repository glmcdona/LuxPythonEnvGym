import sys
import os
from setuptools import setup, find_packages

setup(
    name='luxai2021',
    version='0.1.0',
    author='Geoff McDonald',
    author_email='glmcdona@gmail.com',
    packages=find_packages(exclude=['tests*']),
    url='http://pypi.python.org/pypi/luxai2021/',
    license='MIT',
    description='Matching python environment code for Lux AI 2021 Kaggle competition and a gym interface for RL models',
    long_description=open('README.md').read(),
    install_requires=[
        "pytest",
        "stable_baselines3==1.2.1a2",
        "numpy",
        "tensorboard",
        "gym==0.19.0"
    ],
    package_data={'luxai2021': ['game/game_constants.json', 'env/rng/rng.js', 'env/rng/seedrandom.js']},
    test_suite='nose2.collector.collector',
    tests_require=['nose2'],
)


if sys.version_info < (3,7) or sys.version_info >= (3,8):
    os.system("")
    class style():
        YELLOW = '\033[93m'
    version = str(sys.version_info.major) + "." + str(sys.version_info.minor)
    message = f'/!\ Warning, python{version} detected, you will need to use python3.7 to submit to kaggle.'
    message = style.YELLOW + message
    print(message)
