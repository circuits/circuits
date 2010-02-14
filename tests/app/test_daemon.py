#!/usr/bin/env python

import os
from signal import SIGTERM
from subprocess import call

from tests.app import app

def test():
    pidfile = os.path.join(os.getcwd(), "app.pid")
    status = call(["python", app.__file__, pidfile])

    assert status == 0

    f = open(pidfile, "r")
    pid = int(f.read().strip())
    f.close()

    os.kill(pid, SIGTERM)

    assert True
    os.remove(pidfile)
