#!/usr/bin/env python


import pytest
if pytest.PLATFORM == "win32":
    pytest.skip("Unsupported Platform")


import sys
from os import kill
from time import sleep
from errno import ESRCH
from signal import SIGTERM
from subprocess import Popen


from . import app


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
    tmpdir.ensure("app.pid")
    pid_path = tmpdir.join("app.pid")

    args = [sys.executable, app.__file__, str(pid_path)]
    Popen(args, env={'PYTHONPATH': ':'.join(sys.path)}).wait()

    sleep(1)

    assert pid_path.check(exists=True, file=True)

    pid = None
    with pid_path.open() as f:
        pid = int(f.read().strip())

    assert isinstance(pid, int)
    assert pid > 0

    kill(pid, SIGTERM)
    wait(pid)
