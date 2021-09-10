"""
This downloads two required python package dependencies that are not pre-installed
by Kaggle yet.

This places the following two packages in the current working directory:
    luxai2021
    stable_baselines3
"""

import os
import shutil
import subprocess
import tempfile

def localize_package(git, branch, folder):
    if os.path.exists(folder):
        print("Already localized %s" % folder)
    else:
        # https://stackoverflow.com/questions/51239168/how-to-download-single-file-from-a-git-repository-using-python
        # Create temporary dir
        t = tempfile.mkdtemp()

        args = ['git', 'clone', '--depth=1', git, t]
        res = subprocess.Popen(args, stdout=subprocess.PIPE)
        output, _error = res.communicate()

        if not _error:
            print(output)
        else:
            print(_error)
        
        # Copy desired file from temporary dir
        shutil.move(os.path.join(t, folder), '.')
        # Remove temporary dir
        shutil.rmtree(t, ignore_errors=True)

localize_package('https://github.com/glmcdona/LuxPythonEnvGym.git', 'main', 'luxai2021')
localize_package('https://github.com/DLR-RM/stable-baselines3.git', 'master', 'stable_baselines3')