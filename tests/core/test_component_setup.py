from circuits import Component, Manager
from circuits.core.handlers import handler


"""Component Setup Tests

Tests that event handlers of a Component are
automatically registered as event handlers.
"""


class App(Component):

    def test(self, event, *args, **kwargs):
        pass


class A(Component):
    pass


class B(Component):

    informed = False

    @handler("prepare_unregister", channel="*")
    def _on_prepare_unregister(self, event, c):
        if event.in_subtree(self):
            self.informed = True


class Base(Component):

    channel = "base"


class C(Base):

    channel = "c"


def test_basic():
    m = Manager()

    app = App()
    app.register(m)

    assert app.test in app._handlers.get("test", set())

    app.unregister()
    while len(m):
        m.flush()

    assert not m._handlers


def test_complex():
    m = Manager()

    a = A()
    b = B()

    a.register(m)
    b.register(a)

    assert a in m
    assert a.root == m
    assert a.parent == m
    assert b in a
    assert b.root == m
    assert b.parent == a

    a.unregister()
    while len(m):
        m.flush()

    assert b.informed
    assert a not in m
    assert a.root == a
    assert a.parent == a
    assert b in a
    assert b.root == a
    assert b.parent == a


def test_subclassing_with_custom_channel():
    base = Base()

    assert base.channel == "base"

    c = C()

    assert c.channel == "c"
