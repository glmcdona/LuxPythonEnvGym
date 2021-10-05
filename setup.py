import os
import sys
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
        "stable_baselines3",
        "numpy",
        "tensorboard",
        "gym<0.20.0"
    ],
    package_data={'luxai2021': ['game/game_constants.json', 'env/rng/rng.js', 'env/rng/seedrandom.js']},
    test_suite='nose2.collector.collector',
    tests_require=['nose2'],
)


if sys.version_info < (3,7) or sys.version_info > (3,7):
    os.system("")
    class style():
        YELLOW = '\033[93m'
    print(style.YELLOW+"Warning, you are using python" + str(sys.version_info.major) + "." + str(sys.version_info.minor) + ", to submit to kaggle consider switching to python3.7.")
