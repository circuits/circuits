# Package:  circuits
# Date:     3rd October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Lightweight Event driven and Asynchronous Application Framework

circuits is a **Lightweight** **Event** driven and **Asynchronous**
**Application Framework** for the `Python Programming Language`_
with a strong **Component** Architecture.

:copyright: CopyRight (C) 2004-2011 by James Mills
:license: MIT (See: LICENSE)
"""

__author__ = "James Mills"
__date__ = "12th February 2011"
__version__ = "1.6"

from circuits.core import handler, BaseComponent, Component, Event
from circuits.core import future, Pool, Task, Worker
from circuits.core import Bridge, Debugger, Timer
from circuits.core import Manager

# hghooks: no-pyflakes
