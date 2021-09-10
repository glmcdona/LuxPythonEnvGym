"""
Copied and moidified from here:
https://github.com/Lux-AI-Challenge/Lux-Design-2021/blob/master/kits/cpp/simple/main.py

In a kaggle-environment submission, main.py is loaded into memory and the last function is
searched for. The last function is expected to have args (observation, configuration). Here
we wrap our stdin stdout setup for the agent.

Format of a submission should be:
* submission.tar.gz
    main.py
        (copied from main_kaggle_submission.py)
    main_lux-ai-2021.py
    model.zip
        (the model you want to run)
    /luxai2021/
        (copy of the 'luxai2021' folder from this repo)
    /stable_baselines3/
        (copy of 'stable_baselines3' folder from here https://github.com/DLR-RM/stable-baselines3)
"""

from subprocess import Popen, PIPE
from threading  import Thread
from queue import Queue, Empty

import atexit
import os
import sys
agent_processes = [None, None]
t = None
q = None
def cleanup_process():
    global agent_processes
    for proc in agent_processes:
        if proc is not None:
            proc.kill()
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()
def python_policy_agent(observation, configuration):
    """
    Wrapper for a stdin stdout agent.

    Args:
        observation ([type]): Observation data.
        configuration ([type]): Config data.

    Returns:
        Set of actions to perform.
    """
    global agent_processes, t, q

    agent_process = agent_processes[observation.player]
    ### Do not edit ###
    if agent_process is None:
        if "__raw_path__" in configuration:
            cwd = os.path.dirname(configuration["__raw_path__"])
        else:
            cwd = os.path.dirname(__file__)
        agent_process = Popen(["python3", "./main_lux-ai-2021.py"], stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd)
        agent_processes[observation.player] = agent_process
        atexit.register(cleanup_process)

        # following 4 lines from https://stackoverflow.com/questions/375427/a-non-blocking-read-on-a-subprocess-pipe-in-python
        q = Queue()
        t = Thread(target=enqueue_output, args=(agent_process.stderr, q))
        t.daemon = True # thread dies with the program
        t.start()
    if observation.step == 0:
        # fixes bug where updates array is shared, but the first update is agent dependent actually
        observation["updates"][0] = f"{observation.player}"
    
    # print observations to agent
    agent_process.stdin.write(("\n".join(observation["updates"]) + "\n").encode())
    agent_process.stdin.flush()

    # wait for data written to stdout
    agent1res = (agent_process.stdout.readline()).decode()
    _end_res = (agent_process.stdout.readline()).decode()

    while True:
        try:  line = q.get_nowait()
        except Empty:
            # no standard error received, break
            break
        else:
            # standard error output received, print it out
            print(line.decode(), file=sys.stderr, end='')

    outputs = agent1res.split("\n")[0].split(",")
    actions = []
    for cmd in outputs:
        if cmd != "":
            actions.append(cmd)
    return actions