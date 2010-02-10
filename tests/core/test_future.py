#!/usr/bin/python -i

from time import sleep

from circuits import future, Event, Component, Manager

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

m = Manager()
app = App()
app.register(m)
m.start()

def test_future_value():
    x = m.push(Delay(2))
    sleep(3)
    m.flush()
    assert x.value == "Hello World!"
