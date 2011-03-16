#!/usr/bin/env python

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

    init_path = tmpdir.ensure("__init__.py")
    f = init_path.open("w")
    f.close()

    foo_path = tmpdir.ensure("foo.py")
    with foo_path.open("w") as f:
        f.write(FOO)

    foo = safeimport("foo")
    assert foo is not None
    assert type(foo) is ModuleType

    s = foo.foo()
    assert s == "Hello World!"

    foo_path = tmpdir.ensure("foo.py")
    with foo_path.open("w") as f:
        f.write(FOOBAR)

    import pdb
    pdb.set_trace()

    foo = safeimport("foo")
    assert foo is None
    assert foo not in sys.modules
