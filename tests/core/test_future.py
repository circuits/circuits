#!/usr/bin/python -i

from circuits import future, Event, Component

class Hello(Event):
    "Hello Event"

class Future(Event):
    "Future Event"

class App(Component):

    def hello(self):
        return "Hello World!"

    @future()
    def future(self):
        return self.push(Hello())

def test_future_value():
    app = App()
    while app:
        app.flush()
    x = app.push(Future())
    app.flush()
    app.flush()
    assert x.value == "Hello World!"
