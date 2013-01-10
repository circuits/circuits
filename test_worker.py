#!/usr/bin/python -i


from os import getpid
from time import sleep

from circuits import future
from circuits import Component, Debugger, Event, Manager, Task, Worker


def e():
    return x * 2


def f(*args, **kwargs):
    sleep(3)
    return "Hello from {0:d} {1:s} {2:s}".format(
        getpid(), repr(args), repr(kwargs)
    )


Task.success = True
Task.failure = True


class FooBar(Event):
    """FooBar Event"""


class App(Component):

    @future(process=True)
    def foo_bar(self):
        return "FooBar! {0:d}".format(getpid())


m = Manager() + App() + Worker(process=True) + Debugger()
m.start()
