#!/usr/bin/env python

import os
import errno
import sys
from time import sleep
from signal import SIGTERM
from subprocess import Popen

from tests.app import app


def test(tmpdir):
    tmpdir.ensure("app.pid")
    pid_path = tmpdir.join("app.pid")

    args = [sys.executable, app.__file__, str(pid_path)]
    status = Popen(args, env={'PYTHONPATH': ':'.join(sys.path)}).wait()

    sleep(1)

    assert pid_path.check(exists=True, file=True)

    pid = None
    with pid_path.open() as f:
        pid = int(f.read().strip())

    assert isinstance(pid, int)
    assert pid > 0

    os.kill(pid, SIGTERM)
    try:
        os.waitpid(pid, os.WTERMSIG(0))
    except OSError as e:
        assert e.args[0] == errno.ECHILD
