#!/usr/bin/python -i

from os import getpid

from circuits import Component, Debugger, Event, Manager


class Hello(Event):
    """Hello Event"""


class App(Component):

    def hello(self):
        return "Hello World! ({0:d})".format(getpid())


m = Manager() + Debugger()
m.start()
App().start(process=True, link=m)
