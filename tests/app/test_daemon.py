#!/usr/bin/env python

import os
from signal import SIGTERM
from subprocess import Popen

from tests.app import app

def test(coverage):
    pidfile = os.path.join(os.getcwd(), "app.pid")

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
    assert True

    os.remove(pidfile)

    coverage.combine()
