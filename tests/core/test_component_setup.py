# Module:   test_component_setup
# Date:     23rd February 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Component Setup Tests

Tests that filters and listeners of a Component are
automatically registered as event handlers.
"""

from circuits import Component, Manager

class App(Component):

    def test(self, event, *args, **kwargs):
        pass

class A(Component):
    pass

class B(Component):
    pass

class Base(Component):

    channel = "base"

class C(Base):

    channel = "c"

def test_basic():
    m = Manager()

    app = App()
    app.register(m)

    assert app.test in m.channels.get(("*", "test"), [])

    app.unregister()

    assert not m._handlers

def test_complex():
    m = Manager()

    a = A()
    b = B()

    a.register(m)
    b.register(a)

    assert a in m
    assert a.root == m
    assert a.manager == m
    assert b in a
    assert b.root == m
    assert b.manager == a

    a.unregister()

    assert a not in m
    assert a.root == a
    assert a.manager == a
    assert b in a
    assert b.root == a
    assert b.manager == a

def test_subclassing_with_custom_channel():
    base = Base()

    assert base.channel == "base"

    c = C()

    assert c.channel == "c"
