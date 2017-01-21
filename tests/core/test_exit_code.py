#!/usr/bin/env python
import sys
from subprocess import PIPE, Popen

from circuits.six import b

from . import exitcodeapp


def test_ints(tmpdir):
    for expected_status in range(4):
        args = [sys.executable, exitcodeapp.__file__,
                "{0:d}".format(expected_status)]
        p = Popen(args, env={"PYTHONPATH": ":".join(sys.path)})
        status = p.wait()

        assert status == expected_status


def test_string(tmpdir):
    args = [sys.executable, exitcodeapp.__file__, "foobar"]
    p = Popen(args, env={"PYTHONPATH": ":".join(sys.path)}, stderr=PIPE)
    status = p.wait()

    assert status == 1
    assert p.stderr.read() == b("foobar\n")
