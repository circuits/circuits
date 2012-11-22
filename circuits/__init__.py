# Package:  circuits
# Date:     3rd October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Lightweight Event driven and Asynchronous Application Framework

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

:copyright: CopyRight (C) 2004-2012 by James Mills
:license: MIT (See: LICENSE)

.. _Python Programming Language: http://www.python.org/
"""

__author__ = "James Mills"
__date__ = "22nd November 2012"
__version__ = "2.0.0"

from circuits.core import future, Pool, Task, Worker
from circuits.core import Debugger, Loader, Manager, Timer
from circuits.core import handler, tick, BaseComponent, Component
from circuits.core import BaseEvent, DerivedEvent, Event, LiteralEvent

# hghooks: no-pyflakes
