import pytest
from circuits import future, Event, Component


class App(Component):

    @future()
    def foo(self):
        for _ in xrange(100000):
            pass
        return 1

    def hello(self):
        a = yield self.call(Event.create("foo"))
        b = yield self.call(Event.create("foo"))
        yield a.value + b.value

    def bar(self):
        x = yield self.call(Event.create("hello"))
        yield x


def test_basic():
    a = App()
    future()
    a.start()
    e = a.fire(Event.create("bar"))
    pytest.wait_for(e, "value", 1)
