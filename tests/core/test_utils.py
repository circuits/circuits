#!/usr/bin/env python
import sys
from types import ModuleType

from circuits import Component
from circuits.core.utils import findchannel, findroot, findtype


FOO = """\
def foo():
    return "Hello World!"
"""

FOOBAR = """\
def foo();
    return "Hello World!'
"""


class Base(Component):

    """Base"""


class App(Base):

    def hello(self):
        return "Hello World!"


class A(Component):

    channel = "a"


class B(Component):

    channel = "b"


def test_safeimport(tmpdir):
    from circuits.core.utils import safeimport

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


def test_findroot():
    app = App()
    a = A()
    b = B()

    b.register(a)
    a.register(app)

    while len(app):
        app.flush()

    root = findroot(b)

    assert root == app


def test_findchannel():
    app = App()
    (A() + B()).register(app)

    while len(app):
        app.flush()

    a = findchannel(app, "a")

    assert a.channel == "a"


def test_findtype():
    app = App()
    (A() + B()).register(app)

    while len(app):
        app.flush()

    a = findtype(app, A)

    assert isinstance(a, A)
