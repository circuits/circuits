#!/usr/bin/python -i


from os import getpid
from time import sleep

from circuits import Debugger, Manager, Task, Map, Pool


def e():
    return x * 2


def f():
    sleep(10)
    return "Hello from {0:d}".format(getpid())


m = Manager() + Pool() + Debugger()
m.start()
