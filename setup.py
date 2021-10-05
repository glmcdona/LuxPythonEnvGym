import sys
from setuptools import setup, find_packages

if sys.version_info < (3,7):
    sys.exit('Sorry, Python < 3.7 is not supported, upgrade to >=3.7, <3.8')

if sys.version_info > (3,7):
    sys.exit('Sorry, Python > 3.7 is not supported, downgrade to >=3.7, <3.8')

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
