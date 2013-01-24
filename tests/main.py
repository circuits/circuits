#!/usr/bin/env python

import sys
from types import ModuleType
from os.path import abspath, dirname
from subprocess import Popen, STDOUT


def importable(module):
    try:
        m = __import__(module, globals(), locals())
        return type(m) is ModuleType
    except ImportError:
        return False


def runtests(version=""):
    cmd = ["py.test", "-r", "fsxX", "--ignore=tmp"]
    if version:
        #Supports testing under different versions of python,
        #assuming that version of python and pytest is installed.
        #In the form "X.Y"
        #Not actually correctly implemented at the moment.
        #The only way to change the version is by changing the version parameter
        #at the function definition.
        cmd[0] = cmd[0] + "-" + version

    if importable("pytest_cov"):
        cmd.append("--cov=circuits")
        cmd.append("--cov-report=html")

    cmd.append(dirname(abspath(__file__)))

    raise SystemExit(Popen(cmd, stdout=sys.stdout, stderr=STDOUT).wait())

if __name__ == "__main__":
    runtests()
