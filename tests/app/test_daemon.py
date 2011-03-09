#!/usr/bin/env python

import os
import errno
from signal import SIGTERM
from subprocess import Popen

import pytest
pytest.importorskip("pytest_cov")

from tests.app import app


def test(tmpdir, cov):
    tmpdir.ensure("app.pid")
    pidpath = tmpdir.join("app.pid")
    pidfile = str(pidpath)

    args = ["python", app.__file__, pidfile]
    cmd = " ".join(args)
    p = Popen(cmd, shell=True)
    status = p.wait()

    assert status == 0

    assert os.path.exists(pidfile)
    assert os.path.isfile(pidfile)

    f = open(pidfile, "r")
    pid = int(f.read().strip())
    f.close()

    os.kill(pid, SIGTERM)
    try:
        os.waitpid(pid, os.WTERMSIG(0))
    except OSError as e:
        assert e[0] == errno.ECHILD

    os.remove(pidfile)

    cov.combine()
