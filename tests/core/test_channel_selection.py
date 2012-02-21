#!/usr/bin/python -i

from circuits import Event, Component, Manager


class Foo(Event):
    """Foo Event"""

    channels = ("a",)


class Bar(Event):
    """Bar Event"""


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
        return self.fire(Bar())

    def bar(self):
        return "Bar"


def test():
    m = Manager() + A() + B() + C()

    while m:
        m.flush()

    # Rely on Event.channels
    x = m.fire(Foo())
    m.flush()
    assert x.value == "Foo"

    # Explicitly specify the channel
    x = m.fire(Foo(), "b")
    m.flush()
    assert x.value == "Hello World!"

    # Explicitly specify a set of channels
    x = m.fire(Foo(), "a", "b")
    m.flush()
    assert x.value == ["Foo", "Hello World!"]

    # Rely on self.channel
    x = m.fire(Foo(), "c")
    m.flush()
    m.flush()
    assert x.value == "Bar"
