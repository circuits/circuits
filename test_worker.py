#!/usr/bin/python -i


from os import getpid
from time import sleep

from circuits import Debugger, Manager, Task, Worker


def e():
    return x * 2


def f():
    sleep(10)
    return "Hello from {0:d}".format(getpid())


m = Manager() + Worker() + Debugger()
m.start()
