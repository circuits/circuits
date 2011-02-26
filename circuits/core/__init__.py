# Package:  core
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Core

This package contains the essential core parts of the circuits framework.
"""

from handlers import handler

from events import Event
from manager import Manager
from components import BaseComponent, Component

from values import Value
from futures import future

from timers import Timer

try:
    from bridge import Bridge
except:
    Bridge = None

from pools import Pool
from workers import Task, Worker
from debugger import Debugger

__all__ = ("handler", "BaseComponent", "Component", "Event",
        "future", "Pool", "Task", "Worker",
        "Bridge", "Debugger", "Timer",
        "Manager",
)

# hghooks: no-pyflakes
