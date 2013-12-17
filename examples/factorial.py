#!/usr/bin/env python

from circuits import task, Worker
from circuits import Component, Debugger


def factorial(n):
    x = 1
    for i in range(1, (n + 1)):
        x = x * (i + 1)
    return x


class App(Component):

    def init(self, *args, **kwargs):
        Worker(process=True).register(self)

    def started(self, component):
        x = yield self.call(task(factorial, 10))
        print("{0:d}".format(x.value))
        self.stop()

app = App()
Debugger().register(app)
app.run()
