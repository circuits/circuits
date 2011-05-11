#!/usr/bin/env python

import os
import sys


def test(tmpdir):
    if not os.name == "posix":
        py.test.skip("Cannot run test on a non-POSIX platform.")

    from time import sleep
    from subprocess import Popen
    from signal import SIGHUP, SIGTERM

    from tests.core import signalapp

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

    os.kill(pid, SIGTERM)
    sleep(1)

    f = open(signalfile, "r")
    signal = f.read().strip()
    f.close()

    assert signal == str(SIGTERM)

    os.remove(pidfile)
    os.remove(signalfile)
