#!/usr/bin/python -i

from circuits import Event, Component, Manager

class A(Event):
    "A Event"

class App(Component):

    def test(self, message):
        return message

m = Manager()
app = App()
app.register(m)
m.start()

def test_fire():
    x = m.push(Event("test"), "test")
    m.flush()
    assert x.value == "test"

def test_contains():
    assert App in m
    assert not m in app
