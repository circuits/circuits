#!/usr/bin/env python


import pytest


import os
import sys
from time import sleep
from errno import ESRCH
from signal import SIGTERM
from os import kill, remove
from subprocess import Popen


from . import signalapp


def is_running(pid):
    try:
        kill(pid, 0)
    except OSError as error:
        if error.errno == ESRCH:
            return False
    return True


def wait(pid, timeout=3):
    count = timeout
    while is_running(pid) and count:
        sleep(1)


def test(tmpdir):
    if not os.name == "posix":
        pytest.skip("Cannot run test on a non-POSIX platform.")

    tmpdir.ensure(".pid")
    tmpdir.ensure(".signal")
    pidfile = str(tmpdir.join(".pid"))
    signalfile = str(tmpdir.join(".signal"))

    args = [sys.executable, signalapp.__file__, pidfile, signalfile]
    cmd = " ".join(args)
    p = Popen(cmd, shell=True, env={'PYTHONPATH': ':'.join(sys.path)})
    status = p.wait()

    assert status == 0

    sleep(1)

    assert os.path.exists(pidfile)
    assert os.path.isfile(pidfile)

    f = open(pidfile, "r")
    pid = int(f.read().strip())
    f.close()

    kill(pid, SIGTERM)
    wait(pid)

    f = open(signalfile, "r")
    signal = f.read().strip()
    f.close()

    assert signal == str(SIGTERM)

    remove(pidfile)
    remove(signalfile)
