#!/usr/bin/env python

import os
import sys
from types import ModuleType
from imp import cache_from_source

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

    os.remove(cache_from_source(str(foo_path)))
    foo_path.write(FOOBAR)

    foo = safeimport("foo")
    assert foo is None
    assert foo not in sys.modules
