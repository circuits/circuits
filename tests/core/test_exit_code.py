#!/usr/bin/env python


import sys
from subprocess import Popen


from . import exitcodeapp


def test(tmpdir):
    for expected_status in range(4):
        args = [sys.executable, exitcodeapp.__file__, "{0:d}".format(expected_status)]
        p = Popen(args, env={"PYTHONPATH": ":".join(sys.path)})
        status = p.wait()

        assert status == expected_status
