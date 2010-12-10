#!/usr/bin/env python

import os

import py
py.test.skip("XXX: Not passing...")

def test(tmpdir, cov):
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

    args = ["python", signalapp.__file__, pidfile, signalfile]
    cmd = " ".join(args)
    p = Popen(cmd, shell=True)
    status = p.wait()

    assert status == 0

    assert os.path.exists(pidfile)
    assert os.path.isfile(pidfile)

    f = open(pidfile, "r")
    pid = int(f.read().strip())
    f.close()

    os.kill(pid, SIGHUP)
    sleep(1)

    f = open(signalfile, "r")
    signal = f.read().strip()
    f.close()

    assert signal == str(SIGHUP)

    os.kill(pid, SIGTERM)
    assert True

    os.remove(pidfile)
    os.remove(signalfile)

    cov.combine()
