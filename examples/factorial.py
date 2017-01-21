#!/usr/bin/env python
from __future__ import print_function

from time import sleep

from circuits import Component, Debugger, Event, Timer, Worker, task


def factorial(n):
    x = 1
    for i in range(1, (n + 1)):
        x = x * (i + 1)
        sleep(1)  # deliberate!
    return x


class App(Component):

    def init(self, *args, **kwargs):
        Worker(process=True).register(self)

    def foo(self):
        print("Foo!")

    def started(self, component):
        Timer(1, Event.create("foo"), persist=True).register(self)
        x = yield self.call(task(factorial, 10))
        print("{0:d}".format(x.value))
        self.stop()


app = App()
Debugger().register(app)
app.run()
