#!/usr/bin/python -i
from circuits import Component, Event, Manager


class foo(Event):

    """foo Event"""

    channels = ("a",)


class bar(Event):

    """bar Event"""


class A(Component):

    channel = "a"

    def foo(self):
        return "Foo"


class B(Component):

    channel = "b"

    def foo(self):
        return "Hello World!"


class C(Component):

    channel = "c"

    def foo(self):
        return self.fire(bar())

    def bar(self):
        return "Bar"


def test():
    m = Manager() + A() + B() + C()

    while len(m):
        m.flush()

    # Rely on Event.channels
    x = m.fire(foo())
    m.flush()
    assert x.value == "Foo"

    # Explicitly specify the channel
    x = m.fire(foo(), "b")
    m.flush()
    assert x.value == "Hello World!"

    # Explicitly specify a set of channels
    x = m.fire(foo(), "a", "b")
    m.flush()
    assert x.value == ["Foo", "Hello World!"]

    # Rely on self.channel
    x = m.fire(foo(), "c")
    m.flush()
    m.flush()
    assert x.value == "Bar"
