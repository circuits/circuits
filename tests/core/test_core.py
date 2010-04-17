#!/usr/bin/python -i

from circuits import Event, Component, Manager

class Test(Event):
    """Test Event"""

class App(Component):

    def test(self):
        return "Hello World!"

m = Manager()
app = App()
app.register(m)

while app: app.flush()

def test_fire():
    x = m.push(Test())
    m.flush()
    assert x.value == "Hello World!"

def test_contains():
    assert App in m
    assert not m in app
