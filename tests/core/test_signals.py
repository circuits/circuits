#!/usr/bin/env python
import os
import sys
from errno import ESRCH
from os import kill, remove
from signal import SIGTERM
from subprocess import Popen
from time import sleep

import pytest

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

    with open(signalfile, "r") as fd:
        signal = fd.read().strip()

    assert int(signal) == int(SIGTERM)

    remove(pidfile)
    remove(signalfile)
