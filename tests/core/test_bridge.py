# Module:   bridge
# Date:     5th November 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Bridge Tests"""

from time import sleep

from circuits import Bridge
from circuits import Event, Component, Manager

class Foo(Component):

    flag = False

    def foo(self):
        self.flag = True

    def dummy(self):
        pass

class Bar(Component):

    flag = False

    def bar(self):
        self.flag = True

    def dummy(self):
        pass


def test():
    m1 = Manager()
    b1 = Bridge(bind=("127.0.0.1", 8000), nodes=[("127.0.0.1", 8001)])
    b1.IgnoreChannels.extend(["dummy"])
    foo = Foo()
    m1 += b1
    m1 += foo
    m1.start()

    m2 = Manager()
    b2 = Bridge(bind=("127.0.0.1", 8001), nodes=[("127.0.0.1", 8000)])
    b2.IgnoreChannels.extend(["dummy"])
    bar = Bar()
    m2 += b2
    m2 += bar
    m2.start()

    m1.push(Event(), "bar")
    m1.push(Event(), "dummy")
    sleep(1)

    assert not foo.flag
    assert bar.flag

    m2.push(Event(), "foo")
    m2.push(Event(), "dummy")
    sleep(1)

    assert foo.flag
    assert bar.flag
