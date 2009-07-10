#!/usr/bin/python -i

"""Artificial Neural Networing Library

...
"""

from circuits import Component, Manager, Debugger
from circuits.core import handler, Event, BaseComponent

class Node(BaseComponent):
    pass

m = Manager() + Debugger()


