#!/usr/bin/env python

import os
import sys
from types import ModuleType

from circuits.core.utils import safeimport

FOO = """\
def foo():
    return "Hello World!"
"""

FOOBAR = """\
def foo();
    return "Hello World!'
"""

from circuits.core.utils import safeimport

def test(tmpdir):
    sys.path.insert(0, str(tmpdir))

    foo_path = tmpdir.ensure("foo.py")
    foo_path.write(FOO)

    foo = safeimport("foo")
    assert foo is not None
    assert type(foo) is ModuleType

    s = foo.foo()
    assert s == "Hello World!"
    pyc = foo_path.new(ext="pyc")
    if pyc.check(file=1):
        pyc.remove(ignore_errors=True)
    pyd = foo_path.dirpath('__pycache__')
    if pyd.check(dir=1):
        pyd.remove(ignore_errors=True)
    foo_path.write(FOOBAR)

    foo = safeimport("foo")
    assert foo is None
    assert foo not in sys.modules
