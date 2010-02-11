#!/usr/bin/python -i

from time import sleep

from circuits import future, Event, Component

class Hello(Event):
    "Hello Event"

class Delay(Event):
    "Delay Event"

class App(Component):

    def hello(self):
        return "Hello World!"

    @future()
    def delay(self, n=1):
        sleep(n)
        return self.push(Hello())

app = App()
app.start()

def test_future_value():
    x = app.push(Delay(2))
    sleep(3)
    app.flush()
    assert x.value == "Hello World!"
