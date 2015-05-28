#!/usr/bin/env python
import pytest

import os
import sys
from time import sleep
from errno import ESRCH
from signal import SIGTERM
from os import kill, remove
from subprocess import Popen


from . import exitcodeapp


def test(tmpdir):
    for code in [0,1,2,3,"test", None]:
        args = [sys.executable, exitcodeapp.__file__, repr(code)]
        p = Popen(cmd, shell=True, env={'PYTHONPATH': ':'.join(sys.path)})
        status = p.wait()

        if isinstance(code, int):
            assert status == code
        elif code is None:
            assert status == 0
        else:
            assert status == 1
