#!/usr/bin/python -i

from circuits import handler, Event, Component, Manager

class Test(Event):
    """Test Event"""

class App(Component):

    @handler("test")
    def test_0(self):
        return 0

    @handler("test", priority=3)
    def test_3(self):
        return 3

    @handler("test", priority=2)
    def test_2(self):
        return 2

m = Manager()
app = App()
app.register(m)

while m: m.flush()

def test():
    v = m.push(Test())
    while m: m.flush()
    x = list(v)
    assert x == [3, 2, 0]
