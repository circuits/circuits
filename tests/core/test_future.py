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

app = App()
app.start()

def test_future_value():
    x = app.push(Future())
    app.flush()
    assert x.value == "Hello World!"
