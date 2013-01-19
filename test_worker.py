#!/usr/bin/python -i


from os import getpid
from time import sleep

from circuits import Debugger, Event, Manager, Task, Worker


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


m = Manager() + Worker(process=True) + Debugger()
m.start()
